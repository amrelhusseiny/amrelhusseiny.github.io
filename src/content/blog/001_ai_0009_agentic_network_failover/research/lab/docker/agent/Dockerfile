FROM python:3.12-slim

LABEL org.opencontainers.image.title="lab-agent"
LABEL org.opencontainers.image.description="LangGraph agents: TypeSafe Jev (decision) + Space Bunny (action) for the dual-path failover lab"

# Same flaky-proxy retry loop as the router image, and it must fail loudly.
RUN set -eu; \
    ok=0; \
    for attempt in $(seq 1 20); do \
      echo "=== apt attempt $attempt ==="; \
      if apt-get -o Acquire::Retries=5 -o Acquire::http::Timeout=30 update >/dev/null 2>&1 \
         && apt-get -o Acquire::Retries=5 -y --no-install-recommends install \
                openssh-client iproute2 ca-certificates >/dev/null 2>&1; then \
        ok=1; break; \
      fi; \
      sleep 5; \
    done; \
    [ "$ok" = "1" ] || { echo 'FATAL: apt never succeeded'; exit 1; }; \
    rm -rf /var/lib/apt/lists/*; \
    ssh -V 2>&1

# Pinned for reproducibility. Cert checks off: the lab egresses through a
# corporate TLS-inspecting proxy, per operator instruction.
RUN set -eu; \
    ok=0; \
    for attempt in $(seq 1 10); do \
      if pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
           httpx langgraph==1.2.12 langchain-core==1.6.5 langchain-openai==1.6.6 >/dev/null 2>&1; then \
        ok=1; break; \
      fi; \
      sleep 5; \
    done; \
    [ "$ok" = "1" ] || { echo 'FATAL: pip never succeeded'; exit 1; }; \
    python3 -c 'import langgraph, langchain_core, langchain_openai, httpx; print("langchain", langchain_core.__version__, "ok")'

COPY ca/ /usr/local/share/ca-certificates/
RUN update-ca-certificates

COPY sitecustomize.py /usr/local/lib/python3.12/site-packages/sitecustomize.py
COPY agent_ed25519 /root/.ssh/agent_ed25519
RUN chmod 600 /root/.ssh/agent_ed25519 && \
    printf 'Host *\n    StrictHostKeyChecking no\n    UserKnownHostsFile /dev/null\n    LogLevel ERROR\n' > /root/.ssh/config && \
    chmod 600 /root/.ssh/config

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

WORKDIR /agent
CMD ["python3", "-u", "monitor.py"]
