#!/usr/bin/env bash
set -euo pipefail
EVROOT="$(dirname "$0")/../evidence"
NODES="peer1 provider1 customer1 provider2 rs1 rsclient1 rsclient2 m1 m2 m3 m4 m5"

dump_node() {
  local node="$1" outdir="$2" prefix="${3:-}"
  mkdir -p "$outdir"
  docker exec "rfc9234-$node" vtysh -c "show bgp summary" > "$outdir/${node}_bgp_summary.txt" 2>&1 || true
  docker exec "rfc9234-$node" vtysh -c "show bgp ipv4 unicast" > "$outdir/${node}_bgp_table.txt" 2>&1 || true
  if [ -n "$prefix" ]; then
    docker exec "rfc9234-$node" vtysh -c "show bgp ipv4 unicast $prefix" > "$outdir/${node}_prefix_detail.txt" 2>&1 || true
  fi
  docker exec "rfc9234-$node" vtysh -c "show bgp neighbors" > "$outdir/${node}_neighbors.txt" 2>&1 || true
}

dump_all() {
  local scenario="$1" prefix="${2:-}"
  local outdir="$EVROOT/$scenario"
  echo "[+] Capturing evidence for scenario: $scenario (12 nodes)"
  for n in $NODES; do
    dump_node "$n" "$outdir" "$prefix"
  done
}

case "${1:-}" in
  all)   dump_all "all-cases" "198.51.100.0/24" ;;
  basic) dump_all "basic" "" ;;
  *)
    echo "Usage: $0 {all|basic}"
    echo "  all   - full capture incl OTC prefix detail on 198.51.100.0/24"
    echo "  basic - summary + table + neighbors per node"
    exit 1
    ;;
esac
