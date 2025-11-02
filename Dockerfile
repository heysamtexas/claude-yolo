# Claude Code YOLO Mode - Secure Docker Environment
# Multi-stage build for optimal layer caching and size

FROM ubuntu:24.04 AS base

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install base dependencies and essential tools
RUN apt-get update && apt-get install -y \
    # Core utilities
    curl \
    wget \
    git \
    jq \
    ripgrep \
    coreutils \
    ca-certificates \
    gnupg \
    lsb-release \
    software-properties-common \
    unzip \
    # Build tools
    build-essential \
    make \
    cmake \
    # Python dependencies
    python3 \
    python3-pip \
    python3-venv \
    # Database client dependencies
    postgresql-client \
    mysql-client \
    redis-tools \
    # Additional utilities
    vim \
    nano \
    tmux \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf aws awscliv2.zip

# Install Google Cloud CLI
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && apt-get update \
    && apt-get install -y google-cloud-cli \
    && rm -rf /var/lib/apt/lists/*

# Install MongoDB Shell
RUN curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg \
    && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list \
    && apt-get update \
    && apt-get install -y mongodb-mongosh \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl - Kubernetes CLI
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/$(dpkg --print-architecture | sed 's/amd64/amd64/;s/arm64/arm64/')/kubectl" \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
    && rm kubectl

# Install Helm - Kubernetes package manager
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Terraform
RUN ARCH=$(dpkg --print-architecture) && \
    wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && \
    apt-get install -y terraform && \
    rm -rf /var/lib/apt/lists/*

# Install Docker CLI and Docker Compose
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# Install k9s - Terminal UI for Kubernetes
RUN ARCH=$(dpkg --print-architecture) && \
    K9S_VERSION=$(curl -s https://api.github.com/repos/derailed/k9s/releases/latest | grep tag_name | cut -d '"' -f 4) && \
    if [ "$ARCH" = "amd64" ]; then \
        K9S_ARCH="amd64"; \
    elif [ "$ARCH" = "arm64" ]; then \
        K9S_ARCH="arm64"; \
    fi && \
    wget https://github.com/derailed/k9s/releases/download/${K9S_VERSION}/k9s_Linux_${K9S_ARCH}.tar.gz && \
    tar -xzf k9s_Linux_${K9S_ARCH}.tar.gz && \
    mv k9s /usr/local/bin/ && \
    rm k9s_Linux_${K9S_ARCH}.tar.gz

# Install yq - YAML processor
RUN ARCH=$(dpkg --print-architecture) && \
    YQ_VERSION=$(curl -s https://api.github.com/repos/mikefarah/yq/releases/latest | grep tag_name | cut -d '"' -f 4) && \
    wget https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/yq_linux_${ARCH} -O /usr/local/bin/yq && \
    chmod +x /usr/local/bin/yq

# Install httpie - User-friendly HTTP client
RUN apt-get update && apt-get install -y httpie && rm -rf /var/lib/apt/lists/*

# Install Trivy - Container & IaC security scanner
RUN ARCH=$(dpkg --print-architecture) && \
    wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor -o /usr/share/keyrings/trivy.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | tee -a /etc/apt/sources.list.d/trivy.list && \
    apt-get update && \
    apt-get install -y trivy && \
    rm -rf /var/lib/apt/lists/*

# Install tfsec - Terraform security scanner
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then \
        TFSEC_ARCH="amd64"; \
    elif [ "$ARCH" = "arm64" ]; then \
        TFSEC_ARCH="arm64"; \
    fi && \
    TFSEC_VERSION=$(curl -s https://api.github.com/repos/aquasecurity/tfsec/releases/latest | grep tag_name | cut -d '"' -f 4) && \
    wget https://github.com/aquasecurity/tfsec/releases/download/${TFSEC_VERSION}/tfsec-linux-${TFSEC_ARCH} -O /usr/local/bin/tfsec && \
    chmod +x /usr/local/bin/tfsec

# Install uv - modern Python package manager
RUN pip3 install --no-cache-dir --break-system-packages uv

# Install Python development tools via uv
RUN uv tool install ruff && \
    uv tool install mypy && \
    uv tool install pytest && \
    uv tool install bandit && \
    uv tool install pre-commit

ENV PATH="/root/.local/bin:${PATH}"

# Install gitleaks for secrets scanning
RUN wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.4/gitleaks_8.18.4_linux_x64.tar.gz \
    && tar -xzf gitleaks_8.18.4_linux_x64.tar.gz \
    && mv gitleaks /usr/local/bin/ \
    && rm gitleaks_8.18.4_linux_x64.tar.gz

# Install detect-secrets
RUN pip3 install --no-cache-dir --break-system-packages detect-secrets

# Install Node.js (for MCP servers and additional tooling)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code (official installation method)
# Note: This will be installed via npm when Claude Code publishes stable releases
# For now, this is a placeholder for the official installation
RUN npm install -g @anthropic-ai/claude-code || echo "Claude Code will be installed via official method"

# Install ttyd for optional web terminal access
# Detect architecture and download appropriate binary
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then \
        TTYD_ARCH="x86_64"; \
    elif [ "$ARCH" = "arm64" ]; then \
        TTYD_ARCH="aarch64"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    wget https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.${TTYD_ARCH} -O /usr/local/bin/ttyd && \
    chmod +x /usr/local/bin/ttyd

# Install Tailscale for optional secure remote access
# Using official installation script which handles all architectures
RUN curl -fsSL https://tailscale.com/install.sh | sh

# Install OpenVPN client for optional corporate VPN connectivity
RUN apt-get update && \
    apt-get install -y openvpn && \
    rm -rf /var/lib/apt/lists/*

# Install cloudflared for Cloudflare Tunnel access
# Using official cloudflare package repository
RUN mkdir -p /usr/share/keyrings && \
    curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/cloudflared.list && \
    apt-get update && \
    apt-get install -y cloudflared && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for safety
# Use UID 1001 to avoid conflicts with Ubuntu 24.04's default UID 1000
RUN useradd -m -s /bin/bash -u 1001 developer

# Create Tailscale and cloudflared directories and set ownership for non-root user
RUN mkdir -p /var/lib/tailscale /var/run/tailscale /home/developer/.cloudflared && \
    chown -R developer:developer /var/lib/tailscale /var/run/tailscale /home/developer/.cloudflared

# Set up working directory
WORKDIR /workspace

# Copy configuration templates (will be copied to user home on first run)
COPY config/ /opt/config-templates/
COPY scripts/ /opt/scripts/
RUN chmod +x /opt/scripts/*.sh

# Switch to non-root user
USER developer

# Default command - init.sh will be sourced via docker-compose
CMD ["/bin/bash"]
