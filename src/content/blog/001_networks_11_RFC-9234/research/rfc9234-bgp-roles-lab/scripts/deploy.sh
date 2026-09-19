#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../topology"
echo "[+] Deploying RFC 9234 showcase lab (12 nodes)..."
docker compose up -d
echo "[+] Waiting for FRR daemons to settle..."
sleep 8
docker compose ps
echo
echo "[+] Done. Connect: docker exec -it rfc9234-<node> vtysh"
echo "    Nodes: peer1 provider1 customer1 provider2 rs1 rsclient1 rsclient2 m1 m2 m3 m4 m5"
