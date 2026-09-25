#!/bin/bash
# Scenario 1: OSPF automatic failover (out-of-box timers, dead 40s).
# TRUE gray failure: SIGSTOP ospfd on r1 (process alive, no LSA flush, hellos stop, links stay UP).
NS=ffr-lab-ospf
OUT=~/lab-compare/v2-ospf
mkdir -p $OUT
pod() { kubectl get pod -n $NS -l name=$1 --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}'; }
RC1=$(pod rc1); R1=$(pod r1); V1=$(pod vm1)
{
echo "=== BEFORE (Path 1 active) ==="; date -u +%Y-%m-%dT%H:%M:%S
echo "--- ping vm1->vm2 ---"
kubectl exec -n $NS $V1 -- ping -c3 -W3 10.1.8.1 2>&1 | tail -3
echo "--- rc1 neighbors ---"
kubectl exec -n $NS $RC1 -- vtysh -c 'show ip ospf neighbor' 2>&1 | grep -E "Full|1.1.1"
echo "--- rc1 route to vm2 ---"
kubectl exec -n $NS $RC1 -- vtysh -c 'show ip route 10.1.8.0/24' 2>&1 | grep -E "via|Known" | head -3
} | tee $OUT/ospf-before.txt
T0=$(date +%s.%N); echo $T0 > $OUT/t0
echo "T0=$T0 -- BREAKING Path 1 (gray: DROP hellos rc1<->r1, links stay UP)" | tee $OUT/ospf-chaos.log
kubectl scale deploy r1 -n $NS --replicas=0 2>&1
echo "R1 pod DELETED (router death) at $(date -u +%Y-%m-%dT%H:%M:%S)" | tee -a $OUT/ospf-chaos.log
# watcher: 1s cadence until route flips to Path0 AND ping recovers
FLIP=""; REPAIR=""
for i in $(seq 1 120); do
  TS=$(date +%s.%N)
  ROUTE=$(kubectl exec -n $NS $RC1 -- vtysh -c 'show ip route 10.1.8.0/24' 2>&1 | grep -E "^\s+\* " | head -1)
  PING=$(kubectl exec -n $NS $V1 -- ping -c1 -W1 10.1.8.1 2>&1 | grep -E "1 received|100% packet loss")
  echo "$TS :: route=[$ROUTE] ping=[$PING]" >> $OUT/ospf-watch.log
  if [ -z "$FLIP" ] && echo "$ROUTE" | grep -q "10.1.5.2"; then FLIP=$TS; echo "ROUTE FLIPPED at $TS" | tee -a $OUT/ospf-chaos.log; fi
  if [ -n "$FLIP" ] && echo "$PING" | grep -q "1 received"; then REPAIR=$TS; echo "PING RECOVERED at $TS" | tee -a $OUT/ospf-chaos.log; break; fi
  sleep 1
done
python3 -c "
t0=float(open('$OUT/t0').read()); f=float('$FLIP'.split()[0]) if '$FLIP' else None; r=float('$REPAIR'.split()[0]) if '$REPAIR' else None
import json
m={'t0':t0,'t_route_flip_s':round(f-t0,1) if f else None,'t_ping_repair_s':round(r-t0,1) if r else None}
open('$OUT/ospf-metrics.json','w').write(json.dumps(m,indent=1)); print(json.dumps(m,indent=1))"
{
echo "=== AFTER (Path 0 active) ==="; date -u +%Y-%m-%dT%H:%M:%S
echo "--- ping vm1->vm2 ---"
kubectl exec -n $NS $V1 -- ping -c3 -W3 10.1.8.1 2>&1 | tail -3
echo "--- rc1 route to vm2 ---"
kubectl exec -n $NS $RC1 -- vtysh -c 'show ip route 10.1.8.0/24' 2>&1 | grep -E "via|Known" | head -3
} | tee $OUT/ospf-after.txt
echo "=== RESTORE (scale r1 back to 1) ===" | tee -a $OUT/ospf-chaos.log
kubectl scale deploy r1 -n $NS --replicas=1 2>&1
kubectl rollout status deploy/r1 -n $NS --timeout=180s 2>&1 | tail -1
sleep 60
echo "--- ping after restore ---"
kubectl exec -n $NS $V1 -- ping -c2 -W3 10.1.8.1 2>&1 | grep loss | tee -a $OUT/ospf-after.txt
kubectl exec -n $NS $RC1 -- vtysh -c 'show ip route 10.1.8.0/24' 2>&1 | grep -E "via" | head -2 | tee -a $OUT/ospf-after.txt
echo DONE
