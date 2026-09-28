FROM python:3.12-slim

LABEL org.opencontainers.image.title="lab-router"
LABEL org.opencontainers.image.description="FRR router with sshd for the dual-path failover lab"

RUN apt-get update && apt-get install -y --no-install-recommends \
      frr \
      openssh-server \
      iproute2 \
      procps \
      ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/sshd /var/log/frr /root/.ssh \
 && ssh-keygen -A \
 && printf 'PermitRootLogin prohibit-password\nPasswordAuthentication no\nPubkeyAuthentication yes\n' > /etc/ssh/sshd_config.d/lab.conf \
 && chmod 700 /root/.ssh

COPY agent_ed25519.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
