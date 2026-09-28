FROM python:3.12-slim

LABEL org.opencontainers.image.title="lab-agent"
LABEL org.opencontainers.image.description="LangGraph agents: TypeSafe Jev (decision) + Space Bunny (action) for the dual-path failover lab"

RUN apt-get update && apt-get install -y --no-install-recommends \
      openssh-client \
      iproute2 \
      ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Pinned for reproducibility. Cert checks off: the lab egresses through a
# corporate TLS-inspecting proxy, per operator instruction.
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
      httpx \
      langgraph==1.2.12 \
      langchain-core==1.6.5 \
      langchain-openai==1.6.6

# The outbound TLS-inspecting proxy (Forcepoint) presents certificates signed
# by a corporate CA.
COPY ca/ /usr/local/share/ca-certificates/
RUN update-ca-certificates

COPY agent_ed25519 /root/.ssh/agent_ed25519
RUN chmod 600 /root/.ssh/agent_ed25519 && \
    printf 'Host *\n    StrictHostKeyChecking no\n    UserKnownHostsFile /dev/null\n    LogLevel ERROR\n' > /root/.ssh/config && \
    chmod 600 /root/.ssh/config

WORKDIR /agent
CMD ["python3", "-u", "monitor.py"]
