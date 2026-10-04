#!/bin/bash
# Idempotent starter for the topology JSON server.
#
# Grafana's Node Graph panel needs frames with id / source / target fields,
# which Prometheus time series do not have, so the shape is generated here
# from the same probe scripts the metrics come from.
#
# Binds 127.0.0.1 plus the monitoring bridge address so the Grafana container
# can reach it. NOT 0.0.0.0: that would publish the lab on the corporate LAN.
#
# The health check looks for real probe output rather than just HTTP 200,
# because the server answers 200 with a warming_up body until the first poll
# lands, and an HTTP-only check declares success before anything works.
DIR=$(cd "$(dirname "$0")" && pwd)
LOG=/tmp/topology-server.log

ready() {
  curl -sf -m 8 "$1/agt/nodes" 2>/dev/null | grep -q '"id"'
}

if ready http://127.0.0.1:8888; then
  echo '  already listening'
  exit 0
fi

GW=$(docker network inspect monitoring_monitoring \
     --format '{{range .IPAM.Config}}{{.Gateway}}{{end}}' 2>/dev/null)
if [ -z "$GW" ]; then
  echo '  monitoring network not found; is the monitoring stack up?'
  exit 1
fi

cd "$DIR"
TOPO_BRIDGE=$GW setsid nohup python3 topology-json.py > "$LOG" 2>&1 < /dev/null &

# The first poll SSHes into six routers, so allow more than a token wait.
for _ in $(seq 1 30); do
  if ready "http://$GW:8888"; then
    echo "  started; loopback and bridge $GW both serve real data"
    exit 0
  fi
  sleep 2
done

echo '  FAILED to produce data; log:'
tail -8 "$LOG" | sed 's/^/    /'
exit 1
