#!/bin/bash
# Keep metrics/lab.influx fresh. Every 5s matches the Prometheus scrape
# interval so the dashboard never shows a stale value.
#
# The file is appended to, never replaced, because telegraf tails it and a mv
# would change the inode out from under the tailer.
#
# It also rotates: an hour of lab runs appends a few hundred thousand lines,
# which is harmless for Loki retention but not worth keeping forever.
D=$(cd "$(dirname "$0")" && pwd)
F=$D/metrics/lab.influx
MAX=$((200 * 1024))   # 200k lines

while true; do
  bash "$D/collect.sh" 2>/dev/null
  if [ -f "$F" ]; then
    LINES=$(wc -l < "$F" 2>/dev/null || echo 0)
    if [ "$LINES" -gt "$MAX" ]; then
      # Truncate in place to keep the same inode, so the tailer survives.
      tail -n 1000 "$F" > "$F.tmp" && cat "$F.tmp" > "$F" && rm -f "$F.tmp"
    fi
  fi
  sleep 5
done
