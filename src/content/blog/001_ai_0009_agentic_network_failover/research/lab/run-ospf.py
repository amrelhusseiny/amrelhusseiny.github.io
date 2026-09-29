#!/usr/bin/env python3
'''
run-ospf.py - OSPF failover measurement, both fault variants.

The OSPF lab needs no API access, so it can be measured completely even
while the agent side is blocked.

Two fault variants, because they measure different things:

  kill : docker stop -t 0 on r1. The veth pair is destroyed, so rc1s peer
         interface goes down immediately and OSPF never waits its dead
         interval. This is interface-down detection, not convergence.

  link : r1s interfaces are set down from INSIDE r1, so the container stays
         alive and the link still looks up from rc1s point of view. OSPF
         has to run the real dead interval. This is the honest number.
'''
import argparse
import json
import os
import subprocess
import sys
import time
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PFX = "ospf"
FWD = "10.91.8.1"
SRC = "10.91.1.1"
RECOVER_MAX_S = 300


def sh(cmd, timeout=120):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           timeout=timeout)
        return p.stdout.strip()
    except subprocess.TimeoutExpired:
        return '(timeout)'
    except Exception as e:
        return '(error %s)' % e


def ping_once():
    out = sh("docker exec %s-rc1 ping -I %s -c 1 -W 1 %s" % (PFX, SRC, FWD), timeout=20)
    return '100% packet loss' not in out and 'bytes from' in out


def wait_healthy(need=5, max_s=200):
    t0 = time.time()
    streak = 0
    while time.time() - t0 < max_s:
        if ping_once():
            streak += 1
            if streak >= need:
                print("    healthy after %.0fs" % (time.time() - t0))
                return True
        else:
            streak = 0
        time.sleep(1)
    print("    NOT healthy after %ds" % max_s)
    return False


def reset():
    # Explicitly remove the containers first. A router just stopped with
    # 'docker stop -t 0' leaves its container object behind, and compose
    # --force-recreate silently skips it, so the next repetition quietly
    # measures a lab that is missing a router. That happened, and it produced
    # four meaningless recovery numbers before the preconditions caught it.
    names = ' '.join('%s-%s' % (PFX, n) for n in NODES)
    sh('docker rm -f %s >/dev/null 2>&1' % names, timeout=120)
    sh('cd ' + HERE + ' && docker compose -f docker-compose.ospf.yml up -d rc1 r1 r2 rc2 r3 r4 2>&1 | tail -1', timeout=300)


def neighbours():
    return sh("docker exec %s-rc1 vtysh -c 'show ip ospf neighbor'" % PFX, timeout=20)

def route():
    return sh("docker exec %s-rc1 vtysh -c 'show ip route'" % PFX, timeout=20)


def r1_ifaces():
    out = sh("docker exec %s-r1 ip -o link show | awk -F': ' '{print $2}'" % PFX)
    return [i.split("@")[0] for i in out.split() if i and i != "lo"]


def apply_fault(mode):
    '''Returns once the fault is fully in place, so T0 is honest.'''
    if mode == "kill":
        sh('docker stop -t 0 %s-r1 >/dev/null 2>&1' % PFX, timeout=30)
        for _ in range(40):
            st = sh("docker inspect %s-r1 --format '{{.State.Running}}'" % PFX,
               timeout=20)
            if st.strip() == "false":
                return "container stopped (peer interface goes down with it)"
            time.sleep(0.25)
        return "container did not stop in time"
    # link: keep the container alive, drop the interfaces from inside it, so
    # the link still looks UP on rc1 and OSPF must wait its dead interval
    ifs = r1_ifaces()
    for i in ifs:
        sh('docker exec %s-r1 ip link set %s down' % (PFX, i), timeout=20)
    time.sleep(1)
    return "interfaces %s set down from inside r1 (container alive)" % ",".join(ifs)


def run_rep(mode, rep):
    stamp = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    run_dir = os.path.join(HERE, 'runs', 'ospf-%s-rep%d-%s' % (mode, rep, stamp))
    os.makedirs(run_dir, exist_ok=True)
    sys.path.insert(0, HERE)
    from recorder import Recorder
    rec = Recorder(run_dir)

    print('  resetting the OSPF lab')
    reset()
    rec.event('waiting for convergence')
    if not wait_all_up():
        rec.event('ABORT: routers did not all come up')
        return None
    if not wait_primary():
        rec.event('ABORT: primary path not in use, measurement meaningless')
        return None
    if not wait_healthy():
        rec.event('ABORT: lab never became healthy')
        return None
    rec.snapshot()
    rec.start_pings()
    time.sleep(4)

    rec.event('applying fault: %s' % mode)
    detail = apply_fault(mode)
    rec.event('fault in place: %s' % detail)
    t0 = rec.mark_t0()
    rec.event('neighbours at T0:\n%s' % neighbours())
    rec.block('rc1 ip-route at T0', route())

    rec.event('waiting for traffic to return')
    t_start = time.time()
    recovered = None
    while time.time() - t_start < RECOVER_MAX_S:
        if ping_once():
            recovered = round(time.time() - t0, 3)
            rec.event('traffic restored at +%.2fs' % recovered)
            break
        time.sleep(1)
    if recovered is None:
        rec.event('DID NOT recover within %ds' % RECOVER_MAX_S)
    rec.block('rc1 ip-route after', route())
    rec.block('rc1 ospf-neighbour after', neighbours())
    time.sleep(2)
    rec.stop_pings()
    rec.collect_pings()
    analysis = rec.analyze()
    json.dump({'mode': mode, 'rep': rep, 'detail': detail,
              'wall_clock_recovery_s': recovered},
             open(os.path.join(run_dir, 'rep.json'), 'w'), indent=2)
    return recovered, analysis


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--modes", default="kill,link")
    args = ap.parse_args()
    summary = []
    for mode in args.modes.split(","):
        mode = mode.strip()
        for rep in range(1, args.reps + 1):
            print('')
            print('=== OSPF / %s / rep %d ===' % (mode, rep))
            out = run_rep(mode, rep)
            if not out:
                continue
            recovered, analysis = out
            for key in sorted(analysis):
                a = analysis[key]
                if a.get('outage'):
                    print('    %-12s downtime=%-9s first_fail=+%ss failed=%s'
                          % (key, a['downtime_s'], a['first_fail_offset_s'],
                             a['failed_probes']))
            summary.append({'mode': mode, 'rep': rep,
                           'wall_clock_recovery_s': recovered,
                           'downtime': analysis})
    path = os.path.join(HERE, 'runs', 'ospf-summary.json')
    json.dump(summary, open(path, 'w'), indent=2)
    print('')
    print('summary -> %s' % path)






# ---- preconditions -------------------------------------------------
NODES = ["rc1", "r1", "r2", "rc2", "r3", "r4"]
PRIMARY_NEXTHOP = "10.91.10.12"
SERVER_NET = "10.91.8.1"


def container_running(name):
    st = sh("docker inspect %s --format '{{.State.Running}}'" % name, timeout=20)
    return st.strip() == "true"


def wait_all_up(max_s=120):
    # The harness must not assume its own preconditions. A previous fault can
    # leave r1 stopped, and a standby-only network fails the very measurement
    # we are trying to take. This was a real silent failure.
    t0 = time.time()
    missing = [n for n in NODES]
    while time.time() - t0 < max_s:
        missing = [n for n in NODES
                   if not container_running("%s-%s" % (PFX, n))]
        if not missing:
            print("    all 6 routers up")
            return True
        time.sleep(2)
    print("    STILL DOWN after %ds: %s" % (max_s, missing))
    return False


def primary_in_use():
    # rc1 must be reaching the server network THROUGH r1 before r1 is killed,
    # otherwise the run measures nothing.
    r = sh("docker exec %s-rc1 vtysh -c 'show ip route'" % PFX, timeout=20)
    for line in r.splitlines():
        if SERVER_NET in line and PRIMARY_NEXTHOP in line:
            return True
    print("    PRECONDITION FAILED: rc1 is not routing to %s via r1 (%s)"
          % (SERVER_NET, PRIMARY_NEXTHOP))
    for line in r.splitlines():
        if SERVER_NET in line:
            print("      actual: %s" % line.strip())
    return False


def r1_ifaces():
    out = sh("docker exec %s-r1 ip -o link show" % PFX, timeout=20)
    names = []
    for line in out.splitlines():
        if ": " not in line:
            continue
        name = line.split(": ", 1)[1].split(":")[0].split("@")[0]
        if name and name != "lo":
            names.append(name)
    return names


def wait_primary(max_s=90):
    # OSPF needs a few seconds after boot to install the primary route.
    t0 = time.time()
    while time.time() - t0 < max_s:
        if primary_in_use():
            print("    primary path in use via %s (%.0fs)"
                  % (PRIMARY_NEXTHOP, time.time() - t0))
            return True
        time.sleep(2)
    return False

if __name__ == '__main__':
    main()
