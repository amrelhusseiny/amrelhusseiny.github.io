#!/bin/bash
# Canonical failback Path0 -> Path1. For each router: remove EVERY 10.1.x static
# (both paths' next-hops; misses are ignored), then install the exact Path-1 set.
# Idempotent: converges from ANY state (agent plans vary run to run).
NS=ffr-lab
pod() { kubectl get pod -n $NS -l name=$1 --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}'; }
RC1=$(pod rc1); R1=$(pod r1); R2=$(pod r2); RC2=$(pod rc2); V1=$(pod vm1)
NOS=""
for net in 10.1.1.0/24 10.1.2.0/24 10.1.3.0/24 10.1.4.0/24 10.1.8.0/24; do
  for nh in 10.1.2.1 10.1.2.2 10.1.3.1 10.1.3.2 10.1.4.1 10.1.4.254 10.1.5.1 10.1.5.2 10.1.6.1 10.1.6.2 10.1.7.1 10.1.7.2; do
    NOS="$NOS -c 'no ip route $net $nh'"
  done
done
apply() { kubectl exec -n $NS $1 -- vtysh -c 'configure terminal' $NOS $(printf " -c '%s'" "$@") -c 'end' -c 'write memory' 2>&1 | grep -viE "warning|note|refusing|building|integrated|OK" | head -3; shift; }
echo "--- tunnels up ---"
kubectl exec -n $NS $RC1 -- ip link set gre-r1 up 2>&1
kubectl exec -n $NS $R1 -- ip link set gre-rc1 up 2>&1
echo "--- canonical Path-1 tables ---"
kubectl exec -n $NS $RC1 -- vtysh -c 'configure terminal' $NOS -c 'ip route 10.1.3.0/24 10.1.2.2' -c 'ip route 10.1.4.0/24 10.1.2.2' -c 'ip route 10.1.8.0/24 10.1.2.2' -c 'end' -c 'write memory' 2>&1 | grep -viE "warning|note|refusing|building|integrated|OK" | head -3
kubectl exec -n $NS $R1 -- vtysh -c 'configure terminal' $NOS -c 'ip route 10.1.1.0/24 10.1.2.1' -c 'ip route 10.1.4.0/24 10.1.3.2' -c 'ip route 10.1.8.0/24 10.1.3.2' -c 'end' -c 'write memory' 2>&1 | grep -viE "warning|note|refusing|building|integrated|OK" | head -3
kubectl exec -n $NS $R2 -- vtysh -c 'configure terminal' $NOS -c 'ip route 10.1.1.0/24 10.1.3.1' -c 'ip route 10.1.2.0/24 10.1.3.1' -c 'ip route 10.1.8.0/24 10.1.4.254' -c 'end' -c 'write memory' 2>&1 | grep -viE "warning|note|refusing|building|integrated|OK" | head -3
kubectl exec -n $NS $RC2 -- vtysh -c 'configure terminal' $NOS -c 'ip route 10.1.1.0/24 10.1.4.1' -c 'ip route 10.1.2.0/24 10.1.4.1' -c 'ip route 10.1.3.0/24 10.1.4.1' -c 'end' -c 'write memory' 2>&1 | grep -viE "warning|note|refusing|building|integrated|OK" | head -3
sleep 3
echo "--- verify: FIBs must be single-nexthop Path1 ---"
for t in "$RC1:rc1" "$R1:r1" "$R2:r2" "$RC2:rc2"; do p=${t%%:*}; n=${t##*:}; echo "--- $n ---"; kubectl exec -n $NS $p -- ip route show proto 196 2>&1; done
kubectl exec -n $NS $V1 -- ping -c3 -W3 10.1.8.1 2>&1 | grep -E "loss"
echo FAILBACK-DONE
