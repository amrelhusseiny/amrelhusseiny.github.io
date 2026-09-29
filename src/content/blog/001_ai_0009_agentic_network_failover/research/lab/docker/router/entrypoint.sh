#!/bin/bash
set -e

NODE="${NODE:-router}"
LOGLEVEL="${LOGLEVEL:-informational}"

mkdir -p /var/log/frr /var/run/sshd /etc/frr
chown -R frr:frr /var/log/frr 2>/dev/null || true

/usr/sbin/sshd
echo "[$NODE] sshd started"

# ICMP redirects are noise: r1 and r2 are legitimate next hops, so the kernel
# keeps telling the edge routers to bypass the path they were given, and every
# redirect is counted as a ping error. FRR config alone does not stop this.
for f in /proc/sys/net/ipv4/conf/*/send_redirects; do echo 0 > "$f" 2>/dev/null || true; done
for f in /proc/sys/net/ipv4/conf/*/accept_redirects; do echo 0 > "$f" 2>/dev/null || true; done

if [ -f /config/daemons ]; then
  cp /config/daemons /etc/frr/daemons
  echo "[$NODE] daemons selected:"
  grep -E '^(zebra|staticd|ospfd|mgmtd)=' /etc/frr/daemons | tr '\n' ' '
  echo
fi

cp /config/frr.conf /etc/frr/frr.conf

# Docker does not attach networks in a guaranteed order, so eth0/eth1/... cannot
# be trusted to mean primary-a/primary-b/... Resolve every named interface from
# the address Docker already assigned to it, using IF_<NAME>=<ip> env vars.
for key in $(env | grep -o '^IF_[A-Z]*' | sort); do
  name=${key#IF_}
  want=$(printenv "$key")
  if [ -z "$want" ]; then continue; fi
  dev=$(ip -4 -o addr show 2>/dev/null | awk -v w="$want" '$4 ~ "^" w "/" {print $2; exit}')
  if [ -n "$dev" ]; then
    echo "[$NODE] $name -> $dev ($want)"
    sed -i "s/__${name}__/$dev/g" /etc/frr/frr.conf 2>/dev/null || true
  else
    echo "[$NODE] WARNING: no interface has address $want (for $name)"
  fi
done


if ! grep -q '^hostname' /etc/frr/frr.conf 2>/dev/null; then
  sed -i "1i hostname $NODE" /etc/frr/frr.conf 2>/dev/null || true
fi
if ! grep -q 'log file' /etc/frr/frr.conf 2>/dev/null; then
  sed -i "2i log file /var/log/frr/frr.log $LOGLEVEL" /etc/frr/frr.conf 2>/dev/null || true
fi
touch /var/log/frr/frr.log && chown frr:frr /var/log/frr/frr.log
chmod 664 /var/log/frr/frr.log

echo "[$NODE] frr.conf:"
cat /etc/frr/frr.conf

/usr/lib/frr/frrinit.sh start || true
sleep 3
echo "[$NODE] running daemons:"
ps -eo comm= | grep -E '^(zebra|staticd|ospfd|mgmtd)$' | sort | tr '\n' ' '
echo
tail -f /dev/null
