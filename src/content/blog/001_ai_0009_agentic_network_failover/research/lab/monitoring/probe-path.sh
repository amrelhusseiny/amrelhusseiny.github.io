#!/bin/bash
# Emit the active path rc1 is using toward the server, for one lab.
# Usage: probe-path.sh <agt|ospf> <server-net>
#
# Output is influx line protocol so telegraf's exec input parses it directly.

LAB=$1
NET=$2

VTY=$(docker exec $LAB-rc1 vtysh -c 'show ip route' 2>/dev/null)
if [ -z "$VTY" ]; then
  echo "path_state,lab=$LAB,device=rc1 active=0i,reachable=0"
  exit 0
fi

# The selected route is the one marked S>* / O>*. Match on the prefix only,
# because FRR prints the address with a /32 suffix.
PREFIX=$(echo "$NET" | cut -d/ -f1)
LINE=$(echo "$VTY" | awk -v p="$PREFIX" '$1 ~ /^[A-Z]>?\*$/ && $2 ~ "^"p {print; exit}')

if [ -z "$LINE" ]; then
  echo "path_state,lab=$LAB,device=rc1 active=0i,reachable=1"
  exit 0
fi

HOP=$(echo "$LINE" | grep -oE 'via [0-9.]+' | head -1 | cut -d' ' -f2)
DEV=$(echo "$LINE" | grep -oE 'eth[0-9]+' | head -1)

# FRR prints [distance/metric] with a space that varies. Pull field 3 and take
# the leading number only, otherwise the digits concatenate (1 and 0 -> 10).
BRACKET=$(echo "$LINE" | awk '{print $3}')
DIST=$(echo "$BRACKET" | sed 's/[^0-9]*\([0-9]*\).*/\1/')

# Reachability of the next hop is probed rather than assumed. When the router
# behind the active path dies, FRR keeps the static route installed and marked
# best because nothing told it otherwise: traffic blackholes while the route
# table still looks perfect. So probe the next hop and report hop_down, which
# is the case a dashboard actually needs to catch.
HOPDEAD=0
if [ -n "$HOP" ]; then
  timeout 3 bash -c "echo > /dev/tcp/$HOP/22" 2>/dev/null || HOPDEAD=1
fi

[ -z "$HOP" ] && HOP=none
[ -z "$DEV" ] && DEV=none
[ -z "$DIST" ] && DIST=0

echo "path_state,lab=$LAB,device=rc1,next_hop=$HOP,out_if=$DEV active=1i,reachable=$((1-HOPDEAD)),hop_down=$HOPDEAD,distance=$DIST"
