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
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent
from typing_extensions import TypedDict

import transport
from models import (UsageCallback, build_bunny_model, build_jev,
                 judge_path, retry_stats)
from tools import TOOLS
from topology import (CLIENT_NET, DEVICES, FRR_LOG, PATH_DIAGRAM,
                     SERVER_NET, TOPOLOGY_PROMPT, is_noise, path_state)
from trail import get_trail

STAGE = {"before": 1, "after": 8}
# 01 jev line verdicts, 02 jev path decision, 03 bunny request,
# 04 bunny transcript, 05 bunny usage, 06 config writes, 07 after-verdicts


class FailoverState(TypedDict, total=False):
    cursors: Dict[str, int]
    items: List[Dict[str, Any]]
    judged_before: List[Dict[str, Any]]
    judged_after: List[Dict[str, Any]]
    faulty_before: List[str]
    faulty_after: List[str]
    chosen_path: Dict[str, Any]
    bunny_result: str
    bunny_transcript: List[Dict[str, Any]]
    conclusion: str
    metrics: Dict[str, Any]


def _probe(item):
    """Read one router: its FRR log and its routing table.

    Runs in a worker thread. The six routers are independent, so reading them
    serially was six sequential SSH round trips for no reason.
    """
    node, ip = item
    rc, out, err, dt = transport.ssh(ip, "cat " + FRR_LOG)
    if rc != 0:
        return node, rc, out, err, None
    route = transport.show(ip, "show ip route")
    return node, rc, out, err, route


def make_capture(tag: str):
    """Read every router over SSH, all six at once. Emits one item per NEW log
    line, plus one item per unreachable router. A per-router cursor means a
    steady-state cycle judges nothing."""

    def capture(state: FailoverState) -> Dict[str, Any]:
        t = get_trail()
        cursors = dict(state.get("cursors") or {})
        items: List[Dict[str, Any]] = []

        t0 = time.time()
        with ThreadPoolExecutor(max_workers=len(DEVICES)) as pool:
            results = list(pool.map(_probe, DEVICES.items()))
        t.log("   probed %d routers in %.2fs" % (len(results), time.time() - t0))

        for node, rc, out, err, route in results:
            ip = DEVICES[node]
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


def make_choose_path():
    """Second Jev call: which path should carry traffic, from a closed set.

    Routing state is read from the devices here rather than assumed, so the
    menu Jev chooses from only contains paths that have a route installed in
    both directions.
    """

    def choose_path(state: FailoverState) -> Dict[str, Any]:
        t = get_trail()
        faulty = state.get("faulty_before") or []

        rc1_obs = transport.show(DEVICES["rc1"], "show ip route")
        rc2_obs = transport.show(DEVICES["rc2"], "show ip route")
        t.evidence("rc1", "path-rc1.txt", rc1_obs)
        t.evidence("rc2", "path-rc2.txt", rc2_obs)

        rc1_rows = path_state("rc1", rc1_obs, SERVER_NET)
        rc2_rows = path_state("rc2", rc2_obs, CLIENT_NET)
        t.log("path state rc1: %s"
              % [(r["path"], r["distance"], r["active"]) for r in rc1_rows])
        t.log("path state rc2: %s"
              % [(r["path"], r["distance"], r["active"]) for r in rc2_rows])

        decision = judge_path(faulty, rc1_rows, rc2_rows, PATH_DIAGRAM)
        t.write(3, "jev-path-decision", decision)
        t.log("JEV[path] chose %s (confidence %s)"
              % (decision["path"], decision["confidence"]))
        return {"chosen_path": decision}

    return choose_path
def make_bunny(agent):
    """Hand the chosen path to Space Bunny.

    Option C. Jev decides which router failed and which path should carry the
    traffic. Space Bunny decides HOW to make that change safely, then verifies
    it. It no longer re-derives the topology, which is where most of the
    previous 23-call wall clock went.
    """

    def bunny(state: FailoverState) -> Dict[str, Any]:
        t = get_trail()
        judged = state.get("judged_before") or []
        faulty = state.get("faulty_before") or []
        decision = state.get("chosen_path") or {}
        target = decision.get("path")
        bad = [j for j in judged if j["choice"] == "failed"]

        L = ["",
             "A monitoring agent (TypeSafe Jev) read the routers and judged "
             "each log line on its own. These lines were judged FAILED:",
             ""]
        for j in bad:
            L.append("  %-4s  %s" % (j["node"], j["line"]))
        L += ["",
              "Routers judged faulty: %s" % (", ".join(faulty) or "none"),
              "",
              "Jev then chose which path should carry the traffic:",
              "  %s  (%s)" % (target, decision.get("label", "?")),
              "",
              PATH_DIAGRAM,
              "",
              "Which path is already decided. Your job is HOW to make the "
              "routers actually carry traffic over it, safely, without "
              "stranding the return path.",
              "",
              "How to be fast and correct:",
              "  * Issue independent read-only commands together in one turn, "
              "    not one per turn.",
              "  * Do not explore the topology. It is given above.",
              "  * Read the routing table on rc1 and rc2 before changing "
              "    anything.",
              "  * A non-zero exit on a command means the syntax was "
              "    rejected. That is a syntax error, not a network fault. Fix "
              "    the command; do not change strategy.",
              "  * After every change, read the table back and confirm the "
              "    target path is now the active one.",
              "",
              "What is wrong, and how can you fix it?"]
        user = chr(10).join(L)

        t.write(4, "bunny-request", {"system": TOPOLOGY_PROMPT, "user": user})
        t.log("handing %d faulty line(s) to Space Bunny, path decided: %s"
              % (len(bad), target))

        usage_cb = UsageCallback()
        res = agent.invoke({"messages": [("user", user)]},
                           {"recursion_limit": 40, "callbacks": [usage_cb]})

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

        t.write(6, "bunny-usage", {"usage": usage_cb.report(),
                                   "api_retries": retry_stats()})
        t.log("   bunny usage: %s" % usage_cb.report())
        t.write(5, "bunny-transcript",
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
    g.add_node("choose_path", make_choose_path())
    g.add_node("bunny", make_bunny(agent))
    g.add_node("capture_after", make_capture("after"))
    g.add_node("judge_after", make_judge("after"))
    g.add_node("conclude_healthy", _conclude_healthy)
    g.add_node("conclude_after", _conclude_after)

    g.add_edge(START, "capture")
    g.add_edge("capture", "judge")
    g.add_conditional_edges(
        "judge", _route,
        {"healthy": "conclude_healthy", "faulty": "choose_path"})
    g.add_edge("conclude_healthy", END)
    g.add_edge("choose_path", "bunny")
    g.add_edge("bunny", "capture_after")
    g.add_edge("capture_after", "judge_after")
    g.add_edge("judge_after", "conclude_after")
    g.add_edge("conclude_after", END)
    return g.compile()
