#!/usr/bin/env python3
'''
run-comparison.py - one matched failover repetition across both labs.

Same fault into both labs at the same instant, both measured by the same
external ICMP observer. Nothing is self-reported.
'''
import argparse
import glob
import json
import os
import subprocess
import sys
import time
import datetime

HERE = "/home/aeuu0328/Github/production/personal/amrelhusseiny.github.io/src/content/blog/001_ai_0009_agentic_network_failover/research/lab"

LABS = {
    "agent": {"pfx": "agt", "fwd": "10.90.8.1", "src": "10.90.1.1"},
    "ospf":  {"pfx": "ospf", "fwd": "10.91.8.1", "src": "10.91.1.1"},
}

AGENT_MAX_S = 900
RECOVER_MAX_S = 900


def sh(cmd, timeout=120):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           timeout=timeout)
        return p.stdout.strip()
    except subprocess.TimeoutExpired:
        return '(timeout)'
    except Exception as e:
        return '(error %s)' % e


def ping_once(lab):
    c = LABS[lab]
    out = sh("docker exec %s-rc1 ping -I %s -c 1 -W 1 %s"
          % (c["pfx"], c["src"], c["fwd"]), timeout=20)
    return '100% packet loss' not in out and 'bytes from' in out


def wait_healthy(lab, need=5, max_s=200):
    t0 = time.time()
    streak = 0
    while time.time() - t0 < max_s:
        if ping_once(lab):
            streak += 1
            if streak >= need:
                print('    %s healthy after %.0fs' % (lab, time.time() - t0))
                return True
        else:
            streak = 0
        time.sleep(1)
    print('    %s NOT healthy after %ds' % (lab, max_s))
    return False


def wait_recovered(lab, max_s):
    t0 = time.time()
    while time.time() - t0 < max_s:
        if ping_once(lab):
            print('    %s recovered after %.1fs' % (lab, time.time() - t0))
            return round(time.time() - t0, 2)
        time.sleep(1)
    print('    %s DID NOT recover within %ds' % (lab, max_s))
    return None


def router_is_down(name):
    st = sh("docker inspect %s --format '{{.State.Running}}'" % name, timeout=20)
    return st.strip() == 'false'


def kill_router(name):
    # -t 0 so the router dies instantly: a real router does not linger for
    # docker's 10 second SIGTERM grace period.
    sh('docker stop -t 0 %s >/dev/null 2>&1' % name, timeout=30)
    for _ in range(40):
        if router_is_down(name):
            return True
        time.sleep(0.25)
    return False


def light_telemetry(rec):
    # Kept deliberately cheap: a heavy snapshot loop starved the ping
    # processes and punched holes in the downtime measurement.
    for lab, c in LABS.items():
        for n in ("rc1", "rc2"):
            cont = "%s-%s" % (c["pfx"], n)
            rec.block("%s %s ip-route" % (lab, cont),
                     sh("docker exec %s vtysh -c 'show ip route'" % cont, timeout=20))
        if lab == "ospf":
            cont = "%s-rc1" % c["pfx"]
            rec.block("ospf rc1 ospf-neighbor",
                     sh("docker exec %s vtysh -c 'show ip ospf neighbor'" % cont,
                        timeout=20))


# The repetition currently being measured. reset_labs() runs before each one
# and needs to know where to archive the previous bundle.
CURRENT_REP_DIR = [None]


def _archive_agent_bundle(wait_s=240):
    """Copy the finished agent bundle into runs/<rep>/agent-trail.

    Three things went wrong here before this worked, all worth recording.

    Timing: the harness records recovery the moment traffic flows again, but
    the agent keeps working for another ten seconds and writes its transcript
    and token usage at the very end. Archiving on recovery silently dropped
    05-bunny-transcript and 06-bunny-usage.

    Waiting on pgrep did not work: the agent image ships no procps, so pgrep
    exits 127, the shell falls through to the DONE branch, and the wait
    returns instantly while the agent is still running.

    The sentinel path: trail.finalize() writes 07-metrics.json under trail/,
    not at the bundle root. Globbing the root made the loop spin for the full
    timeout and archive nothing.

    Source: /agent/out is a bind mount of ./out on the host, so copy from the
    host rather than shelling into the container to tar.
    """
    dst = CURRENT_REP_DIR[0]
    if not dst:
        return
    src = os.path.join(HERE, "out")
    sentinel = os.path.join(src, "*", "trail", "07-metrics.json")
    t0 = time.time()
    while time.time() - t0 < wait_s:
        if glob.glob(sentinel):
            break
        time.sleep(2)
    else:
        print("    WARNING: agent did not finalise within %ds" % wait_s)
    dst = os.path.join(dst, "agent-trail")
    os.makedirs(dst, exist_ok=True)
    if os.path.isdir(src):
        sh("cp -a %s/. %s/" % (src, dst), timeout=120)


def reset_labs():
    """Remove the routers explicitly, then bring both labs up.

    A router just stopped with docker stop -t 0 leaves its container object
    behind and compose --force-recreate silently skips it, so the next
    repetition would measure a lab that is missing a router. That produced four
    meaningless recovery numbers before the preconditions caught it.
    """
    for pfx in ('agt', 'ospf'):
        names = ' '.join('%s-%s' % (pfx, n)
                         for n in ('rc1', 'r1', 'r2', 'rc2', 'r3', 'r4'))
        sh('docker rm -f %s >/dev/null 2>&1' % names, timeout=120)
    sh('cd ' + HERE + ' && docker compose -f docker-compose.agent.yml up -d'
       ' rc1 r1 r2 rc2 r3 r4 agent 2>&1 | tail -1', timeout=300)
    sh('cd ' + HERE + ' && docker compose -f docker-compose.ospf.yml up -d'
       ' rc1 r1 r2 rc2 r3 r4 2>&1 | tail -1', timeout=300)
    sh("docker exec agt-agent sh -c 'rm -rf /agent/out/* /agent/__pycache__'",
       timeout=60)
    sh('docker exec agt-agent python3 /agent/seed-cursors.py', timeout=180)


def start_agent():
    # No --reset-cursors: cursors are seeded during reset, so the run judges
    # only the lines the fault actually produced. One or two Jev calls instead
    # of thirty-four, which is what makes the agent survivable against this proxy.
    cmd = "cd /agent && python3 -u monitor.py --out /agent/out > /agent/run.log 2>&1"
    sh("docker exec -d agt-agent sh -c %s" % json.dumps(cmd), timeout=30)
    print("    agents started (LangGraph: Jev decide, Space Bunny act)")


NODES = ['rc1', 'r1', 'r2', 'rc2', 'r3', 'r4']
# where each lab's edge router must be sending traffic BEFORE the fault is
# injected, otherwise the run measures a network that is already on standby
EXPECT_NEXTHOP = {'agt': '10.90.10.12', 'ospf': '10.91.10.12'}
SERVER_NET = {'agt': '10.90.8.1', 'ospf': '10.91.8.1'}


def container_running(name):
    st = sh("docker inspect %s --format '{{.State.Running}}'" % name, timeout=20)
    return st.strip() == 'true'


def wait_all_up(pfx, max_s=150):
    t0 = time.time()
    while time.time() - t0 < max_s:
        missing = [n for n in NODES
                   if not container_running('%s-%s' % (pfx, n))]
        if not missing:
            return True
        time.sleep(2)
    print('    %s STILL DOWN: %s' % (pfx, missing))
    return False


def primary_in_use(pfx, max_s=120):
    net = SERVER_NET[pfx]
    nh = EXPECT_NEXTHOP[pfx]
    t0 = time.time()
    while time.time() - t0 < max_s:
        r = sh("docker exec %s-rc1 vtysh -c 'show ip route'" % pfx, timeout=20)
        for line in r.splitlines():
            if net in line and nh in line:
                return True
        time.sleep(2)
    print('    PRECONDITION FAILED %s: rc1 is not routing to %s via %s'
          % (pfx, net, nh))
    for line in r.splitlines():
        if net in line:
            print('      actual: %s' % line.strip())
    return False



class PreconditionFailed(Exception):
    pass


def run_rep(rep):
    stamp = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    run_dir = os.path.join(HERE, 'runs', 'rep%d-%s' % (rep, stamp))
    CURRENT_REP_DIR[0] = run_dir
    os.makedirs(run_dir, exist_ok=True)

    sys.path.insert(0, HERE)
    from recorder import Recorder
    rec = Recorder(run_dir)

    # --- phase 1: identical baseline ---
    reset_labs()
    rec.event('phase 1: waiting for both labs to converge')
    for lab in ('ospf', 'agent'):
        wait_healthy(lab)
    # Preconditions. Without these a rep can silently measure a lab that is
    # already running on standby, or one whose router never came back, and
    # both look like a good recovery time. Four of the first six OSPF reps
    # were meaningless for exactly that reason.
    for pfx in ('ospf', 'agt'):
        if not wait_all_up(pfx):
            rec.event('ABORT ' + pfx + ': router did not come back')
            raise PreconditionFailed(pfx + ': router down after reset')
        if not primary_in_use(pfx):
            rec.event('ABORT ' + pfx + ': primary path not in use')
            raise PreconditionFailed(pfx + ': rc1 not on the primary next hop')
    rec.snapshot()

  # --- phase 2: observe ---
    rec.start_pings()
    time.sleep(3)

  # --- phase 3: the fault, identical in both labs ---
    rec.event('phase 3: killing r1 in both labs (-t 0, no grace)')
    for lab, c in LABS.items():
        kill_router('%s-r1' % c['pfx'])
    # T0 only AFTER both routers are confirmed dead, otherwise the docker
    # stop grace window is billed to the healthy network
    t0 = rec.mark_t0()

  # --- phase 4: the agent acts ---
    time.sleep(1)
    rec.event('phase 4: starting the agents')
    start_agent()

  # --- phase 5: wait for recovery in both labs ---
    rec.event('phase 5: waiting for both labs to pass traffic again')
    results = {}
    last_tel = time.time()
    t_start = time.time()
    while time.time() - t_start < RECOVER_MAX_S:
        if time.time() - last_tel > 5:
            light_telemetry(rec)
            last_tel = time.time()
        done = all(k in results for k in ('agent', 'ospf'))
        if not done:
            for lab in ('ospf', 'agent'):
                if lab not in results and ping_once(lab):
                    results[lab] = round(time.time() - t_start, 2)
                    rec.event('%s traffic restored at +%.2fs' % (lab, results[lab]))
        else:
            break
        time.sleep(1)

  # --- phase 6: collect ---
    rec.event('phase 6: collecting')
    time.sleep(3)
    light_telemetry(rec)
    rec.snapshot()
    rec.stop_pings()
    rec.collect_pings()
    analysis = rec.analyze()
    _archive_agent_bundle()
    json.dump({'rep': rep, 'wall_clock_recovery': results},
              open(os.path.join(run_dir, 'rep.json'), 'w'), indent=2)
    return run_dir, results, analysis


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--start", type=int, default=1)
    args = ap.parse_args()
    os.makedirs(os.path.join(HERE, "runs"), exist_ok=True)
    summaries = []
    for rep in range(args.start, args.start + args.reps):
        print('')
        print('=== repetition %d ===' % rep)
        try:
            run_dir, wall, analysis = run_rep(rep)
        except PreconditionFailed as e:
            # A rep that could not establish its baseline is not a fast
            # recovery, it is a broken lab. Record it as failed and move on
            # rather than folding a meaningless number into the comparison.
            print('  REP %d ABORTED: %s' % (rep, e))
            summaries.append({'rep': rep, 'status': 'aborted',
                             'reason': str(e)})
            continue
        print('  --- rep %d result ---' % rep)
        for key in sorted(analysis):
            a = analysis[key]
            if a.get('outage'):
                print('    %-12s downtime=%-9s failed_probes=%s'
                      % (key, a['downtime_s'], a['failed_probes']))
            else:
                print('    %-12s no outage' % key)
        summaries.append({'rep': rep, 'status': 'ok', 'dir': run_dir,
                         'wall_clock_recovery': wall,
                         'downtime': analysis})
    path = os.path.join(HERE, 'runs', 'summary.json')
    json.dump(summaries, open(path, 'w'), indent=2)
    print('')
    print('summary written to %s' % path)


if __name__ == '__main__':
    main()
