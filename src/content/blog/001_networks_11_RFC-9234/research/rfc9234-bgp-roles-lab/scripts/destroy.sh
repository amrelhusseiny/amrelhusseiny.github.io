#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../topology"
echo "[+] Tearing down RFC 9234 FRR lab..."
docker compose down -v
