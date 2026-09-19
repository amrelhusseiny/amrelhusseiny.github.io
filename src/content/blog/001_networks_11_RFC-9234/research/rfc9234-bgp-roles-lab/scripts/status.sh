#!/usr/bin/env bash
set -euo pipefail
NODES="peer1 provider1 customer1 provider2 rs1 rsclient1 rsclient2 m1 m2 m3 m4 m5"
for n in $NODES; do
  echo "===== $n : show bgp summary ====="
  docker exec "rfc9234-$n" vtysh -c "show bgp summary" 2>&1 | grep -v vtysh.conf || echo "(node not reachable)"
  echo
done
