FROM python:3.12-slim

LABEL org.opencontainers.image.title="lab-router"
LABEL org.opencontainers.image.description="FRR router with sshd for the dual-path failover lab"

# The corporate egress proxy intermittently 401s or truncates Debian fetches, so
# the install is retried. The trailing assertions make the build FAIL rather than
# silently produce an image that is missing frr, sshd or ping.
RUN set -eu; \
    ok=0; \
    for attempt in $(seq 1 20); do \
      echo "=== apt attempt $attempt ==="; \
      if apt-get -o Acquire::Retries=5 -o Acquire::http::Timeout=30 update >/dev/null 2>&1 \
         && apt-get -o Acquire::Retries=5 -y --no-install-recommends install \
                frr openssh-server iproute2 iputils-ping procps ca-certificates >/dev/null 2>&1; then \
        ok=1; break; \
      fi; \
      sleep 5; \
    done; \
    [ "$ok" = "1" ] || { echo 'FATAL: apt never succeeded'; exit 1; }; \
    rm -rf /var/lib/apt/lists/*; \
    frr --version | head -1; \
    ping -V 2>&1 | head -1; \
    ls -1 /usr/sbin/sshd

RUN mkdir -p /var/run/sshd /var/log/frr /root/.ssh \
 && ssh-keygen -A \
 && printf 'PermitRootLogin prohibit-password\nPasswordAuthentication no\nPubkeyAuthentication yes\n' > /etc/ssh/sshd_config.d/lab.conf \
 && chmod 700 /root/.ssh

COPY sitecustomize.py /usr/local/lib/python3.12/site-packages/sitecustomize.py
COPY agent_ed25519.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Lab-only: never verify TLS certificates anywhere in this container.
# sitecustomize.py patches ssl for every Python caller (httpx, requests,
# urllib3, openai, langchain); the ENV lines cover the non-Python tools.
# There is no env var that disables curl verification, curl still needs -k.
ENV LAB_NO_TLS_VERIFY=1 \
    PYTHONHTTPSVERIFY=0 \
    GIT_SSL_NO_VERIFY=1 \
    NODE_TLS_REJECT_UNAUTHORIZED=0 \
    REQUESTS_CA_BUNDLE= \
    SSL_CERT_FILE= \
    CURL_CA_BUNDLE=

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
