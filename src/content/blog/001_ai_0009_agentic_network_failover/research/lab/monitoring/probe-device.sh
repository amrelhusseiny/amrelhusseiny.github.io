#!/bin/bash
# Emit device liveness for every node in one lab.
# Usage: probe-device.sh <agt|ospf>
#
# Probing every node from one place does not work here, and it is worth
# recording why: rc1 sits only on pa and st, so it has no route to pb or pc
# at all, and r1 has no route to st. Any single vantage point reports most of
# the lab as down. So each node is asked about itself instead: ask the
# device whether its own FRR and sshd are alive. That is independent of
# connectivity and is exactly what the node graph needs.

LAB=$1

for n in rc1 r1 r2 rc2 r3 r4; do
  CID=$LAB-$n
  if ! docker ps --format '{{.Names}}' | grep -qx "$CID"; then
    echo "device_up,lab=$LAB,device=$n up=0i"
    continue
  fi
  F=$(docker exec $CID sh -c 'pidof watchfrr >/dev/null && pidof sshd >/dev/null && echo 1 || echo 0' 2>/dev/null)
  echo "device_up,lab=$LAB,device=$n up=${F:-0}i"
done
