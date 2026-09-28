#!/bin/bash
set -e

NODE="${NODE:-router}"
LOGLEVEL="${LOGLEVEL:-informational}"

mkdir -p /var/log/frr /var/run/sshd /etc/frr
chown -R frr:frr /var/log/frr 2>/dev/null || true

# start sshd in background (so the agent can always get in, even if FRR dies)
/usr/sbin/sshd
echo "[$NODE] sshd started"

# assemble frr.conf: base config from ConfigMap + log line + optional extra
if [ -f /config/frr.conf ]; then cp /config/frr.conf /etc/frr/frr.conf; fi

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

/usr/lib/frr/frrinit.sh start || /usr/lib/frr/zebra -d || true
sleep 2
echo "[$NODE] frr daemons:"
ps aux | grep -E 'zebra|staticd|ospfd' | grep -v grep || echo '  (none)'

tail -f /dev/null
