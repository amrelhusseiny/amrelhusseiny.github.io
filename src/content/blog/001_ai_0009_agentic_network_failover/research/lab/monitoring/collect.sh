#!/bin/bash
# Runs on the HOST, appends influx line protocol to metrics/lab.influx, which
# telegraf tails.
#
# The probes run here rather than inside telegraf because the telegraf image
# has no docker CLI and cannot drive vtysh.
#
# The file is APPENDED to, never replaced. An earlier version built a temp
# file and mv'd it into place, which changed the inode every 5s and left the
# tailer pointed at a file that no longer existed, so Prometheus saw nothing
# at all. Appending keeps one inode and lets tail do its job.
D=$(cd "$(dirname "$0")" && pwd)
OUT=$D/metrics
mkdir -p "$OUT"
F=$OUT/lab.influx
touch "$F"
chmod 666 "$F"

for lab in agt ospf; do
  bash $D/probe-device.sh "$lab" >> "$F" 2>/dev/null
done
bash $D/probe-path.sh agt 10.90.8.1  >> "$F" 2>/dev/null
bash $D/probe-path.sh ospf 10.91.8.1 >> "$F" 2>/dev/null
