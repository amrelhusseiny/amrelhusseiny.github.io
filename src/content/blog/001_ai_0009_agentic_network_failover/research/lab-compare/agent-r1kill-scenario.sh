#!/bin/bash
# Scenario 2 (hands-off): kill R1 pod -> Jev monitor detects -> Mercury repairs.
# IDENTICAL failure to the OSPF lab. Fully automated: start agents, snapshot
# BEFORE, delete R1, wait for repaired:true, collect, restore, failback.
NS=ffr-lab
OUT=~/lab-compare/v2-agents
mkdir -p $OUT
pod() { kubectl get pod -n $NS -l name=$1 --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}'; }
JP=$(pod ssh-server)
run() { kubectl exec -n $NS $JP -- sh -c "$1" 2>&1; }
echo "=== agents start ==="
run 'rm -rf /tmp/lab; mkdir -p /tmp/lab/run /tmp/lab/logs; setsid python3 /agents/jev-monitor.py </dev/null >/tmp/lab/logs/jev-monitor.log 2>&1 & setsid python3 /agents/config-agent.py </dev/null >/tmp/lab/logs/config-agent.log 2>&1 & sleep 3; ps | grep "[p]ython3" | wc -l'
V1=$(pod vm1); RC1=$(pod rc1)
{
echo "=== BEFORE (Path 1 active) ==="; date -u +%Y-%m-%dT%H:%M:%S
echo "--- ping vm1->vm2 ---"
kubectl exec -n $NS $V1 -- ping -c3 -W3 10.1.8.1 2>&1 | tail -3
echo "--- rc1 route to vm2 ---"
kubectl exec -n $NS $RC1 -- vtysh -c 'show ip route 10.1.8.0/24' 2>&1 | grep -E "via|Known" | head -3
echo "--- r1 pod ---"
kubectl get pod -n $NS -l name=r1 2>&1 | head -3
} | tee $OUT/before.txt
kubectl exec -n $NS $JP -- sh -c 'date +%s.%N > /tmp/lab/run/t0' 2>&1
T0=$(kubectl exec -n $NS $JP -- cat /tmp/lab/run/t0 2>&1); echo $T0 > $OUT/t0
echo "T0=$T0 -- KILLING R1 pod (router death, identical to OSPF lab)" | tee $OUT/chaos.log
kubectl scale deploy r1 -n $NS --replicas=0 2>&1 | tee -a $OUT/chaos.log
sleep 3
kubectl get pod -n $NS -l name=r1 2>&1 | tee -a $OUT/chaos.log
echo "R1 GONE at $(date -u +%Y-%m-%dT%H:%M:%S)" | tee -a $OUT/chaos.log
for i in $(seq 1 36); do
  M=$(kubectl exec -n $NS $JP -- cat /tmp/lab/run/metrics.json 2>/dev/null)
  R=$(echo "$M" | grep -o '"repaired": [a-z]*'); A=$(echo "$M" | grep -o '"abort_reason": "[a-z_]*"')
  if [ -n "$M" ] && { [ "$R" = '"repaired": true' ] || [ -n "$A" ]; }; then echo "$M" > $OUT/metrics.json; break; fi
  if [ $i -eq 36 ]; then echo "$M" > $OUT/metrics.json; echo "TIMEOUT (see metrics)"; fi
  sleep 10
done
cat $OUT/metrics.json
echo "=== AFTER ==="
{
echo "--- ping vm1->vm2 ---"
kubectl exec -n $NS $(pod vm1) -- ping -c3 -W3 10.1.8.1 2>&1 | tail -3
echo "--- rc1 route to vm2 ---"
kubectl exec -n $NS $(pod rc1) -- vtysh -c 'show ip route 10.1.8.0/24' 2>&1 | grep -E "via|Known" | head -3
} | tee $OUT/after.txt
echo "=== collect agent transcripts ==="
for f in jev-monitor.log config-agent.log; do kubectl exec -n $NS $JP -- cat /tmp/lab/logs/$f > $OUT/$f 2>&1; done
for f in decision.json rendered-plan.json; do kubectl exec -n $NS $JP -- cat /tmp/lab/run/$f > $OUT/$f 2>&1; done
echo "=== RESTORE: r1 back + failback to Path1 ==="
kubectl scale deploy r1 -n $NS --replicas=1 2>&1
kubectl rollout status deploy/r1 -n $NS --timeout=180s 2>&1 | tail -1
bash ~/lab-compare/failback-path1.sh 2>&1 | tail -4
echo DONE
