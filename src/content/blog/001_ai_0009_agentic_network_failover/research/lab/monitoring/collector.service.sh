#!/bin/bash
# Start the host-side metric collector if it is not already running.
#
# The probes live on the host because the telegraf image has no docker CLI,
# so this loop cannot be a compose service. Idempotent, so it is safe to call
# from anywhere: lab bring-up, a monitoring restart, or by hand.
D=$(cd "$(dirname "$0")" && pwd)
if pgrep -f 'collect-loop.sh' >/dev/null 2>&1; then
  echo "collector already running (pid $(pgrep -f 'collect-loop.sh' | head -1))"
  exit 0
fi
nohup setsid bash "$D/collect-loop.sh" > /tmp/lab-collector.log 2>&1 < /dev/null &
sleep 2
echo "collector started (pid $(pgrep -f 'collect-loop.sh' | head -1))"
