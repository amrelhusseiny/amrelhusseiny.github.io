#!/usr/bin/env python3
"""
graph.py - the LangGraph failover workflow.

  START -> capture -> judge -> (healthy -> END)
                             (faulty  -> bunny -> capture_after
                                        -> judge_after -> END)

Jev is the decision maker: every individual log line is judged on its own and
one "failed" verdict is enough to trigger failover. Space Bunny is the actor:
a real ReAct agent with an SSH tool and a vtysh tool, free to investigate and
to change the running configuration.

There are no thresholds to tune, no debounce and no waiting.
"""
import json
from typing import Any, Dict, List

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent
from typing_extensions import TypedDict

import transport
from models import build_bunny_model, build_jev
from tools import TOOLS
from topology import DEVICES, FRR_LOG, TOPOLOGY_PROMPT, is_noise
from trail import get_trail

STAGE = {"before": 1, "after": 8}


class FailoverState(TypedDict, total=False):
    cursors: Dict[str, int]
    items: List[Dict[str, Any]]
    judged_before: List[Dict[str, Any]]
    judged_after: List[Dict[str, Any]]
    faulty_before: List[str]
    faulty_after: List[str]
    bunny_result: str
    bunny_transcript: List[Dict[str, Any]]
    conclusion: str
    metrics: Dict[str, Any]


def make_capture(tag: str):
    """Read every router over SSH. Emits one item per NEW log line, plus one
    item per unreachable router. A per-router cursor means a steady-state cycle
    judges nothing."""

    def capture(state: FailoverState) -> Dict[str, Any]:
        t = get_trail()
        cursors = dict(state.get("cursors") or {})
        items: List[Dict[str, Any]] = []
        for node, ip in DEVICES.items():
            rc, out, err, dt = transport.ssh(ip, "cat " + FRR_LOG)
            if rc != 0:
                reason = (err or "").strip().splitlines()
                reason = reason[-1] if reason else "ssh exit %d" % rc
                items.append({"node": node, "ip": ip, "source": "ssh",
                              "line": "%s %s did not respond to SSH: %s"
                                       % (node, ip, reason)})
                t.evidence(node, tag + "-frr.log",
                           "(unreachable, ssh rc=%d) %s" % (rc, err))
                t.evidence(node, tag + "-route.txt", "(unreachable)")
                continue

            t.evidence(node, tag + "-frr.log", out)
            route = transport.show(ip, "show ip route")
            t.evidence(node, tag + "-route.txt", route)

            kept, withheld = [], 0
            for line in out.splitlines():
                if not line.strip():
                    continue
                if is_noise(line):
                    withheld += 1
                    t.log("   withheld[noise] %-4s %s" % (node, line[:64]))
                    continue
                kept.append(line)

            cur = cursors.get(node, 0)
            if len(kept) < cur:
                t.log("   cursor reset on %s (log shrank %d -> %d)"
                      % (node, cur, len(kept)))
                cur = 0
            new = kept[cur:]
            cursors[node] = len(kept)
            for line in new:
                items.append({"node": node, "ip": ip, "source": "frr_log",
                              "line": line})
            t.log("   capture %-4s total=%-3d new=%-3d withheld=%d"
                  % (node, len(kept), len(new), withheld))
        t.log("capture[%s]: %d item(s) to judge" % (tag, len(items)))
        return {"items": items, "cursors": cursors}

    return capture


def make_judge(tag: str):
    """One Jev call per item. No averaging, no threshold: a single "failed"
    verdict marks that router faulty."""

    def judge(state: FailoverState) -> Dict[str, Any]:
        t = get_trail()
        jev = build_jev()
        items = state.get("items") or []
        judged: List[Dict[str, Any]] = []
        for it in items:
            resp = jev.invoke(it["line"])
            v = json.loads(resp.content)
            rec = dict(it)
            rec.update({"choice": v["choice"], "confidence": v["confidence"],
                        "latency_s": v["latency_s"]})
            judged.append(rec)
            t.log("   jev %-4s %-6s conf=%-5s %s"
                  % (it["node"], v["choice"], v["confidence"], it["line"][:52]))
        t.write(STAGE[tag], "jev-judgements-" + tag,
                {"count": len(judged), "judgements": judged})
        faulty = sorted({j["node"] for j in judged if j["choice"] == "failed"})
        t.log("JEV[%s] verdict: faulty=%s" % (tag, faulty if faulty else "none"))
        return {"judged_" + tag: judged, "faulty_" + tag: faulty}

    return judge


def make_bunny(agent):
    """Hand the failures to Space Bunny and let it work. It gets the topology
    in its system prompt and nothing else: no hypothesis, no template, no
    suggested commands."""

    def bunny(state: FailoverState) -> Dict[str, Any]:
        t = get_trail()
        judged = state.get("judged_before") or []
        faulty = state.get("faulty_before") or []
        bad = [j for j in judged if j["choice"] == "failed"]
        lines = ["",
                 "A monitoring agent (TypeSafe Jev) read the routers and judged "
                 "each log line on its own. These lines were judged FAILED:",
                 ""]
        for j in bad:
            lines.append("  %-4s  %s" % (j["node"], j["line"]))
        lines += ["",
                  "Routers judged faulty: %s" % ", ".join(faulty),
                  "",
                  "What is wrong, and how can you fix it?"]
        user = "\n".join(lines)
        t.write(2, "bunny-request", {"system": TOPOLOGY_PROMPT, "user": user})
        t.log("handing to Space Bunny: %d faulty router(s)" % len(faulty))

        res = agent.invoke({"messages": [("user", user)]},
                           {"recursion_limit": 60})

        transcript = []
        for m in res["messages"]:
            kind = type(m).__name__
            body = m.content if isinstance(m.content, str) else str(m.content)
            entry = {"role": kind, "content": body}
            if getattr(m, "tool_calls", None):
                entry["tool_calls"] = [
                    {"name": tc.get("name"), "args": tc.get("args")}
                    for tc in m.tool_calls]
            transcript.append(entry)
        t.write(3, "bunny-transcript",
                {"turns": len(transcript), "messages": transcript})
        final = res["messages"][-1].content
        t.log("Space Bunny finished after %d message(s)" % len(transcript))
        return {"bunny_result": final, "bunny_transcript": transcript}

    return bunny


def _route(state: FailoverState) -> str:
    return "healthy" if not state.get("faulty_before") else "faulty"


def _conclude_healthy(state: FailoverState) -> Dict[str, Any]:
    t = get_trail()
    t.log("no log line was judged failed - nothing to do")
    return {"conclusion": "healthy_no_action"}


def _conclude_after(state: FailoverState) -> Dict[str, Any]:
    t = get_trail()
    still = state.get("faulty_after") or []
    t.log("post-fix re-read: still faulty=%s" % (still if still else "none"))
    return {"conclusion": "still_faulty" if still else "repaired"}


def build_graph():
    """Wire the workflow. Space Bunny is constructed once, with the topology as
    her system prompt and both tools bound."""
    agent = create_react_agent(build_bunny_model(), TOOLS,
                               prompt=TOPOLOGY_PROMPT)
    g = StateGraph(FailoverState)
    g.add_node("capture", make_capture("before"))
    g.add_node("judge", make_judge("before"))
    g.add_node("bunny", make_bunny(agent))
    g.add_node("capture_after", make_capture("after"))
    g.add_node("judge_after", make_judge("after"))
    g.add_node("conclude_healthy", _conclude_healthy)
    g.add_node("conclude_after", _conclude_after)

    g.add_edge(START, "capture")
    g.add_edge("capture", "judge")
    g.add_conditional_edges(
        "judge", _route,
        {"healthy": "conclude_healthy", "faulty": "bunny"})
    g.add_edge("conclude_healthy", END)
    g.add_edge("bunny", "capture_after")
    g.add_edge("capture_after", "judge_after")
    g.add_edge("judge_after", "conclude_after")
    g.add_edge("conclude_after", END)
    return g.compile()
