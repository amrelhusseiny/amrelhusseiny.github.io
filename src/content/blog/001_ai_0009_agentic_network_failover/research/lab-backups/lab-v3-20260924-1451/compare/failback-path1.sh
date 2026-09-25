#!/bin/bash
# Deterministic failback Path0 -> Path1. Direct kubectl exec into router pods
# (no nested SSH quoting). Idempotent: safe to rerun.
NS=ffr-lab
pod() { kubectl get pod -n $NS -l name=$1 --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}'; }
vc() { kubectl exec -n $NS $1 -- vtysh -c "$2" 2>&1 | grep -v Warning | head -1; }
vcfg() { kubectl exec -n $NS $1 -- vtysh -c 'configure terminal' -c "$2" -c 'end' 2>&1 | grep -v Warning | head -1; }
RC1=$(pod rc1); R1=$(pod r1); R2=$(pod r2); RC2=$(pod rc2); V1=$(pod vm1)
echo "--- tunnels up ---"
kubectl exec -n $NS $RC1 -- ip link set gre-r1 up 2>&1
kubectl exec -n $NS $R1 -- ip link set gre-rc1 up 2>&1
echo "--- rc1 -> Path1 (want .3/.4/.8 via .2.2 only) ---"
for c in "no ip route 10.1.1.0/24 10.1.5.2" "no ip route 10.1.2.0/24 10.1.5.2" "no ip route 10.1.3.0/24 10.1.5.2" "ip route 10.1.3.0/24 10.1.2.2"; do vcfg $RC1 "$c"; done
echo "--- r1 restore ---"
for c in "ip route 10.1.4.0/24 10.1.3.2" "ip route 10.1.8.0/24 10.1.3.2"; do vcfg $R1 "$c"; done
echo "--- r2 restore ---"
for c in "ip route 10.1.1.0/24 10.1.3.1" "ip route 10.1.2.0/24 10.1.3.1" "ip route 10.1.8.0/24 10.1.4.254"; do vcfg $R2 "$c"; done
echo "--- rc2 -> Path1 ---"
for c in "no ip route 10.1.1.0/24 10.1.7.1" "no ip route 10.1.2.0/24 10.1.7.1" "no ip route 10.1.3.0/24 10.1.7.1" "ip route 10.1.1.0/24 10.1.4.1" "ip route 10.1.2.0/24 10.1.4.1" "ip route 10.1.3.0/24 10.1.4.1"; do vcfg $RC2 "$c"; done
for p in $RC1 $R1 $R2 $RC2; do kubectl exec -n $NS $p -- vtysh -c 'write memory' 2>&1 | grep -v Warning | head -1; done
sleep 3
echo "--- verify ---"
kubectl exec -n $NS $V1 -- ping -c2 -W3 10.1.8.1 2>&1 | grep loss
for t in "$RC1:10.1.8.0/24" "$RC2:10.1.1.0/24"; do p=${t%%:*}; n=${t##*:}; echo -n "$n <- "; kubectl exec -n $NS $p -- vtysh -c "show ip route $n" 2>&1 | grep -E "^\s+\*" | head -1; done
echo FAILBACK-DONE
