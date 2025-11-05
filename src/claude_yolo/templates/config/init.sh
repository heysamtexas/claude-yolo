#!/bin/bash
# Claude Code YOLO Mode - Initialization and Logging Setup

# Create log directory structure
mkdir -p /logs/commands
mkdir -p /logs/claude
mkdir -p /logs/git
mkdir -p /logs/safety

# Log file paths
export COMMAND_LOG="/logs/commands/$(date +%Y%m%d-%H%M%S).log"
export CLAUDE_LOG="/logs/claude/session.log"
export GIT_LOG="/logs/git/operations.log"
export SAFETY_LOG="/logs/safety/checks.log"

# Function to log commands with timestamps
log_command() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $@" >> "$COMMAND_LOG"
}

# Function to log safety checks
log_safety() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [SAFETY] $@" >> "$SAFETY_LOG"
}

# ========================================
# FIRST RUN: Copy configuration templates
# ========================================
if [ ! -d "$HOME/.config/git" ]; then
    echo "🔧 First run detected - setting up configuration..."
    log_safety "First run - copying configuration templates"

    # Copy config templates to user home (no-clobber to preserve existing files)
    # Use cp -a to preserve permissions
    cp -an /opt/config-templates/* "$HOME/.config/" 2>/dev/null || true
    # Ensure hooks are executable (in case permissions were lost)
    chmod +x "$HOME/.config/git/hooks"/* 2>/dev/null || true

    # Make scripts available in PATH
    mkdir -p "$HOME/bin"
    ln -sf /opt/scripts/* "$HOME/bin/" 2>/dev/null || true

    echo "✅ Configuration templates copied"
    log_safety "Configuration templates copied to ~/.config"
else
    log_safety "Using existing configuration"
fi

# Update tmux config only if it doesn't exist (preserve user customizations)
if [ -f "/opt/config-templates/.tmux.conf" ] && [ ! -f "$HOME/.tmux.conf" ]; then
    cp /opt/config-templates/.tmux.conf "$HOME/.tmux.conf"
    log_safety "tmux configuration copied to ~/.tmux.conf"
elif [ -f "$HOME/.tmux.conf" ]; then
    log_safety "Using existing tmux configuration"
fi

# Always ensure Claude Code settings are in workspace for YOLO mode
if [ -f "/opt/config-templates/.claude/settings.local.json" ]; then
    mkdir -p /workspace/.claude
    cp /opt/config-templates/.claude/settings.local.json /workspace/.claude/settings.local.json
    log_safety "Claude Code YOLO mode settings copied to /workspace/.claude/"
    echo "🚀 Claude Code YOLO mode enabled (permissionless)"
fi

# Ensure scripts are in PATH
export PATH="$HOME/bin:$HOME/.local/bin:$PATH"

# ========================================
# GIT CONFIGURATION - Hybrid Approach
# ========================================
if [ ! -f "$HOME/.gitconfig" ]; then
    echo ""
    echo "🔧 Setting up git configuration..."

    # Try to copy from host mount first
    if [ -f "/mnt/host-gitconfig/.gitconfig" ]; then
        echo "  Copying git config from host..."
        cp /mnt/host-gitconfig/.gitconfig "$HOME/.gitconfig"
        echo "  ✅ Git config copied from host"
        log_safety "Git config copied from host mount"
    else
        # Check if we're in detached/web terminal mode
        if [ "$WEBTERMINAL_ENABLED" = "true" ] || [ ! -t 0 ] || [ -z "$TERM" ] || [ "$TERM" = "dumb" ]; then
            # Non-interactive mode - use defaults
            echo "  No host git config found - using defaults"
            echo "  ⚠️  Configure git later with: git config --global user.name 'Your Name'"
            echo "  ⚠️                           git config --global user.email 'your@email.com'"

            git config --global user.name "Developer"
            git config --global user.email "developer@localhost"

            log_safety "Git config created with defaults (non-interactive mode)"
        else
            # Interactive mode - we have a real terminal
            echo "  No host git config found - interactive setup"
            echo ""
            read -p "  Enter your git name (e.g., 'John Doe'): " git_name
            read -p "  Enter your git email (e.g., 'john@example.com'): " git_email

            git config --global user.name "$git_name"
            git config --global user.email "$git_email"

            echo "  ✅ Git config created"
            log_safety "Git config created interactively: $git_name <$git_email>"
        fi
    fi

    # Set up additional git defaults
    git config --global init.defaultBranch main
    git config --global pull.rebase false
else
    log_safety "Using existing git config"
fi

# Always set hooks path (in case config was copied from host without this)
git config --global core.hooksPath "$HOME/.config/git/hooks"
log_safety "Git hooks path configured"

# Welcome message
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║           Claude Code - YOLO Mode (Safe Edition)         ║
║                                                           ║
║  Environment ready with full tooling and safety features ║
║  Logs: /logs (shared with host)                          ║
╚═══════════════════════════════════════════════════════════╝
EOF

echo ""
echo "Logging enabled:"
echo "  Commands: $COMMAND_LOG"
echo "  Claude:   $CLAUDE_LOG"
echo "  Git:      $GIT_LOG"
echo "  Safety:   $SAFETY_LOG"
echo ""

# Set up command logging wrapper (optional - captures bash history)
if [ "$ENABLE_COMMAND_LOGGING" = "true" ]; then
    touch ~/.bash_history
    export PROMPT_COMMAND='history -a; tail -n1 ~/.bash_history 2>/dev/null >> '"$COMMAND_LOG"
    log_safety "Command logging enabled"
fi

# Run initial safety check
log_safety "Container initialized - running safety checks"

# Check for secrets in workspace
if command -v gitleaks &> /dev/null; then
    log_safety "Secrets scanner (gitleaks) available"
fi

# Check for pre-commit
if command -v pre-commit &> /dev/null; then
    log_safety "Pre-commit hooks available"
fi

# Display available tools
echo "Available tools:"
echo "  Python:     $(python3 --version 2>&1 | head -n1)"
echo "  uv:         $(uv --version 2>&1 || echo 'not found')"
echo "  ruff:       $(ruff --version 2>&1 || echo 'not found')"
echo ""
echo "Cloud & Git:"
echo "  git:        $(git --version)"
echo "  gh:         $(gh --version 2>&1 | head -n1)"
echo "  aws:        $(aws --version 2>&1 || echo 'not configured')"
echo "  gcloud:     $(gcloud --version 2>&1 | head -n1 || echo 'not configured')"
echo "  az:         $(az version --output tsv 2>&1 | head -n1 || echo 'not configured')"
echo ""
echo "DevOps & IaC:"
echo "  kubectl:    $(kubectl version --client --short 2>&1 | head -n1 || echo 'not found')"
echo "  helm:       $(helm version --short 2>&1 || echo 'not found')"
echo "  terraform:  $(terraform version 2>&1 | head -n1 || echo 'not found')"
echo "  docker:     $(docker --version 2>&1 || echo 'not found')"
echo "  k9s:        $(k9s version --short 2>&1 || echo 'not found')"
echo ""
echo "Utilities:"
echo "  yq:         $(yq --version 2>&1 || echo 'not found')"
echo "  httpie:     $(http --version 2>&1 || echo 'not found')"
echo ""
echo "Security:"
echo "  trivy:      $(trivy --version 2>&1 | head -n1 || echo 'not found')"
echo "  tfsec:      $(tfsec --version 2>&1 || echo 'not found')"
echo "  gitleaks:   $(gitleaks version 2>&1 || echo 'not found')"
echo ""

log_safety "Initialization complete"

# ========================================
# OPTIONAL: Start web terminal (ttyd)
# ========================================
if [ "$WEBTERMINAL_ENABLED" = "true" ]; then
    echo ""
    echo "🌐 Starting web terminal..."

    # Build ttyd command with options
    TTYD_CMD="ttyd --writable --port ${WEBTERMINAL_PORT:-7681} --interface 0.0.0.0"

    # Add authentication if configured
    if [ -n "$WEBTERMINAL_AUTH" ]; then
        TTYD_CMD="$TTYD_CMD --credential $WEBTERMINAL_AUTH"
        echo "   🔒 Authentication enabled"
    else
        echo "   ⚠️  No authentication (localhost only!)"
    fi

    # Add client options
    TTYD_CMD="$TTYD_CMD --client-option enableZmodem=true"
    TTYD_CMD="$TTYD_CMD --client-option fontSize=16"
    TTYD_CMD="$TTYD_CMD --client-option fontFamily=monospace"
    TTYD_CMD="$TTYD_CMD --client-option theme='{\"background\":\"#1e1e1e\",\"foreground\":\"#d4d4d4\"}'"

    # Start ttyd with tmux for persistent sessions (can disconnect/reconnect)
    # All connections share the same tmux session named "claude-yolo"
    $TTYD_CMD tmux new-session -A -s claude-yolo > /logs/webterminal.log 2>&1 &
    TTYD_PID=$!

    # Wait a moment and check if it started
    sleep 1
    if kill -0 $TTYD_PID 2>/dev/null; then
        echo "   ✅ Web terminal started on port ${WEBTERMINAL_PORT:-7681}"
        echo "   Access at: http://localhost:${WEBTERMINAL_PORT:-7681}"
        log_safety "Web terminal started (PID: $TTYD_PID)"
    else
        echo "   ❌ Failed to start web terminal (check /logs/webterminal.log)"
        log_safety "ERROR: Web terminal failed to start"
    fi
    echo ""
fi

# ========================================
# OPTIONAL: Start Tailscale
# ========================================
if [ -n "$TS_AUTHKEY" ]; then
    echo ""
    echo "🔗 Starting Tailscale..."
    log_safety "Starting Tailscale with hostname: ${TS_HOSTNAME:-claude-yolo}"

    # Start Tailscale daemon in userspace mode (no special privileges needed)
    # Run as background process
    tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock --tun=userspace-networking > /logs/tailscale.log 2>&1 &
    TAILSCALED_PID=$!

    # Wait for daemon to be ready
    sleep 2

    if kill -0 $TAILSCALED_PID 2>/dev/null; then
        echo "   ✅ Tailscale daemon started (PID: $TAILSCALED_PID)"
        log_safety "Tailscale daemon started (PID: $TAILSCALED_PID)"

        # Connect to Tailscale network
        TS_UP_CMD="tailscale up --authkey=$TS_AUTHKEY --hostname=${TS_HOSTNAME:-claude-yolo}"

        # Add accept DNS if configured
        if [ "$TS_ACCEPT_DNS" = "true" ]; then
            TS_UP_CMD="$TS_UP_CMD --accept-dns=true"
        else
            TS_UP_CMD="$TS_UP_CMD --accept-dns=false"
        fi

        # Add any extra arguments
        if [ -n "$TS_EXTRA_ARGS" ]; then
            TS_UP_CMD="$TS_UP_CMD $TS_EXTRA_ARGS"
        fi

        # Execute tailscale up
        $TS_UP_CMD >> /logs/tailscale.log 2>&1

        # Wait a moment and check status
        sleep 2
        TAILSCALE_IP=$(tailscale ip -4 2>/dev/null)

        if [ -n "$TAILSCALE_IP" ]; then
            echo "   ✅ Connected to Tailscale"
            echo "   📍 Tailscale IP: $TAILSCALE_IP"
            echo "   🏷️  Hostname: ${TS_HOSTNAME:-claude-yolo}"
            echo "   🌐 Access from any device on your Tailnet:"
            echo "      http://${TS_HOSTNAME:-claude-yolo}:8000"
            if [ "$WEBTERMINAL_ENABLED" = "true" ]; then
                echo "      http://${TS_HOSTNAME:-claude-yolo}:${WEBTERMINAL_PORT:-7681} (web terminal)"
            fi
            log_safety "Tailscale connected: $TAILSCALE_IP (hostname: ${TS_HOSTNAME:-claude-yolo})"
        else
            echo "   ⚠️  Tailscale started but IP not yet assigned (check /logs/tailscale.log)"
            log_safety "WARNING: Tailscale started but no IP assigned yet"
        fi
    else
        echo "   ❌ Failed to start Tailscale daemon (check /logs/tailscale.log)"
        log_safety "ERROR: Tailscale daemon failed to start"
    fi
    echo ""
else
    log_safety "Tailscale not configured (TS_AUTHKEY not set)"
fi

# ========================================
# OPTIONAL: Start OpenVPN
# ========================================
if [ -n "$OPENVPN_CONFIG" ]; then
    echo ""
    echo "🔒 Starting OpenVPN..."
    log_safety "Starting OpenVPN with config: $OPENVPN_CONFIG"

    # Check if config file exists
    if [ ! -f "/openvpn/$OPENVPN_CONFIG" ]; then
        echo "   ❌ OpenVPN config file not found: /openvpn/$OPENVPN_CONFIG"
        echo "   💡 Make sure your .ovpn file is in the openvpn/ directory"
        log_safety "ERROR: OpenVPN config file not found: /openvpn/$OPENVPN_CONFIG"
    else
        # Create auth file if credentials are provided
        if [ -n "$OPENVPN_AUTH_USER" ] && [ -n "$OPENVPN_AUTH_PASS" ]; then
            echo "   🔑 Using username/password authentication"
            echo "$OPENVPN_AUTH_USER" > /tmp/openvpn-auth.txt
            echo "$OPENVPN_AUTH_PASS" >> /tmp/openvpn-auth.txt
            chmod 600 /tmp/openvpn-auth.txt
            OPENVPN_AUTH_OPT="--auth-user-pass /tmp/openvpn-auth.txt"
            log_safety "OpenVPN configured with username/password auth"
        else
            OPENVPN_AUTH_OPT=""
            log_safety "OpenVPN configured with certificate-based auth"
        fi

        # Start OpenVPN daemon
        sudo openvpn --config "/openvpn/$OPENVPN_CONFIG" \
            $OPENVPN_AUTH_OPT \
            --daemon \
            --log /logs/openvpn.log \
            --verb 3

        # Wait for connection
        echo "   ⏳ Connecting to VPN..."
        sleep 5

        # Check if VPN is connected by looking for tun interface
        if ip addr show | grep -q "tun0"; then
            VPN_IP=$(ip addr show tun0 | grep "inet " | awk '{print $2}' | cut -d/ -f1)
            echo "   ✅ OpenVPN connected"
            echo "   📍 VPN IP: $VPN_IP"
            echo "   🌐 Traffic is now routed through VPN"
            log_safety "OpenVPN connected: $VPN_IP"
        else
            echo "   ⚠️  OpenVPN started but connection not verified"
            echo "      Check /logs/openvpn.log for details"
            log_safety "WARNING: OpenVPN started but tun0 interface not found"
        fi
    fi
    echo ""
else
    log_safety "OpenVPN not configured (OPENVPN_CONFIG not set)"
fi

# ========================================
# OPTIONAL: Start Cloudflared Tunnel
# ========================================
if [ -n "$CLOUDFLARED_TUNNEL_TOKEN" ] || [ -n "$CLOUDFLARED_CONFIG" ]; then
    echo ""
    echo "☁️  Starting Cloudflare Tunnel..."
    log_safety "Starting Cloudflare Tunnel"

    # Determine which connection method to use
    if [ -n "$CLOUDFLARED_TUNNEL_TOKEN" ]; then
        # Token-based authentication (simplest method)
        echo "   🔑 Using tunnel token authentication"
        log_safety "Cloudflared configured with tunnel token"

        # Build cloudflared command
        CLOUDFLARED_CMD="cloudflared tunnel --no-autoupdate run --token $CLOUDFLARED_TUNNEL_TOKEN"

        # Add metrics port if configured
        if [ -n "$CLOUDFLARED_METRICS_PORT" ]; then
            CLOUDFLARED_CMD="$CLOUDFLARED_CMD --metrics 0.0.0.0:$CLOUDFLARED_METRICS_PORT"
            echo "   📊 Metrics enabled on port $CLOUDFLARED_METRICS_PORT"
        fi

        # Start cloudflared daemon
        $CLOUDFLARED_CMD > /logs/cloudflared.log 2>&1 &
        CLOUDFLARED_PID=$!

    elif [ -n "$CLOUDFLARED_CONFIG" ]; then
        # Config file based authentication
        if [ ! -f "/cloudflared/$CLOUDFLARED_CONFIG" ]; then
            echo "   ❌ Cloudflared config file not found: /cloudflared/$CLOUDFLARED_CONFIG"
            echo "   💡 Make sure your config.yml is in the cloudflared/ directory"
            log_safety "ERROR: Cloudflared config file not found: /cloudflared/$CLOUDFLARED_CONFIG"
            CLOUDFLARED_PID=""
        else
            echo "   📄 Using config file: $CLOUDFLARED_CONFIG"
            log_safety "Cloudflared configured with config file: $CLOUDFLARED_CONFIG"

            # Start cloudflared with config file
            cloudflared tunnel --no-autoupdate --config "/cloudflared/$CLOUDFLARED_CONFIG" run > /logs/cloudflared.log 2>&1 &
            CLOUDFLARED_PID=$!
        fi
    fi

    # Check if cloudflared started successfully
    if [ -n "$CLOUDFLARED_PID" ]; then
        # Wait for tunnel to establish
        echo "   ⏳ Establishing tunnel connection..."
        sleep 3

        if kill -0 $CLOUDFLARED_PID 2>/dev/null; then
            echo "   ✅ Cloudflare Tunnel started (PID: $CLOUDFLARED_PID)"
            echo "   🌐 Your services are now accessible via Cloudflare"
            echo "   📋 Check your Cloudflare dashboard for tunnel details"

            if [ "$WEBTERMINAL_ENABLED" = "true" ]; then
                echo "   💡 Tip: Configure tunnel to route to port ${WEBTERMINAL_PORT:-7681} for web terminal access"
            fi

            echo "   📝 Logs: /logs/cloudflared.log"
            log_safety "Cloudflare Tunnel started (PID: $CLOUDFLARED_PID)"
        else
            echo "   ❌ Cloudflare Tunnel failed to start (check /logs/cloudflared.log)"
            log_safety "ERROR: Cloudflare Tunnel failed to start"
        fi
    fi
    echo ""
else
    log_safety "Cloudflare Tunnel not configured (CLOUDFLARED_TUNNEL_TOKEN or CLOUDFLARED_CONFIG not set)"
fi
