# Claude Code YOLO Mode 🚀

Run Claude Code with maximum autonomy, safely isolated in Docker.

Perfect for sales engineers, forward-deployed engineers, and anyone who wants to experiment with Claude Code without risking their host machine.

## Features

✅ **Maximum Safety**
- Container isolation protects your host machine
- Comprehensive secrets scanning (gitleaks, detect-secrets)
- Security scanners for containers and IaC (trivy, tfsec)
- Git hooks prevent dangerous operations
- All actions logged for transparency

✅ **Full DevOps Tooling**
- **Python:** uv, ruff, mypy, pytest, bandit, pre-commit
- **Cloud CLIs:** AWS, Azure, Google Cloud, GitHub
- **Kubernetes:** kubectl, helm, k9s (terminal UI)
- **IaC:** Terraform with security scanning
- **Containers:** Docker CLI, docker-compose
- **Utilities:** yq (YAML), httpie (HTTP client), jq (JSON)
- **Databases:** PostgreSQL, MySQL, Redis, MongoDB clients

✅ **Remote Access**
- Web terminal for browser-based access
- Tailscale integration for secure remote access
- OpenVPN client for corporate VPN connectivity
- Access from phone, tablet, or any device
- Perfect for team sharing and remote work

✅ **Corporate Ready**
- Optional proxy layer for request logging
- Compliance-friendly audit trails
- Resource limits prevent runaway processes
- Permissionless Claude Code mode (baked in)

## Quick Start

### 1. Setup
```bash
# Clone and configure
git clone <this-repo>
cd claude-yolo
make setup  # Auto-detects Colima on macOS!

# Edit .env to adjust resource limits if needed
# Then build and start
make build
make up
```

**Colima/macOS Users:**
- `make setup` auto-configures Docker socket path
- Default limits: 2 CPUs, 4GB RAM (adjust in `.env` if needed)
- Check your Colima allocation: `colima status`
- Increase Colima resources if needed: `colima stop && colima start --cpu 4 --memory 8`

### 2. Enter Container
```bash
docker-compose exec claude-yolo bash
```

**First Run:** On first start, you'll be prompted to set up git (name/email) unless you've configured `HOST_GITCONFIG` in `.env`. Configuration is saved and persists across container restarts.

### 3. Start Coding
```bash
# Set up a new project with safety features
/home/developer/scripts/setup-project-safety.sh /workspace/my-project

# Create Python project
cd /workspace/my-project
uv init .
uv add requests

# Start developing!
```

### 4. Running Web Applications

The container exposes port **8000** by default for web applications:

```bash
# FastAPI example
cd /workspace/my-api
uv init .
uv add fastapi uvicorn

# Create a simple API
cat > main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
EOF

# Run the server
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

**Access your app:**
- Local: http://localhost:8000
- With Tailscale: http://claude-yolo:8000

**Change the port:** Edit `APP_PORT` in `.env` and restart the container.

## Logs

All activity is logged to `./logs/` (shared with host):
- `commands/` - Shell commands with timestamps
- `safety/` - Security checks and warnings
- `git/` - Git operations
- `claude/` - Claude Code session logs

```bash
# Watch logs in real-time
tail -f logs/safety/checks.log
```

## Corporate/Compliance Mode

Enable request logging and inspection:

```bash
# Set proxy env vars in .env first:
# HTTP_PROXY=http://proxy:8080
# HTTPS_PROXY=http://proxy:8080

# Start with proxy profile
make up-proxy
# Or: docker-compose --profile proxy up -d
```

- Web interface: http://localhost:8081
- All HTTP/HTTPS requests logged as JSON
- See `proxy/README.md` for details

## Remote Access Options

### Web Terminal (Browser Access)

Access the container from any web browser - perfect for remote work or mobile devices:

```bash
# Start with web terminal
make up-web

# Access at http://localhost:7681
```

**Features:**
- Browser-based terminal access
- Works on phones, tablets, any device
- Optional password protection
- File upload/download support
- Persistent sessions (tmux)
- See `webterminal/README.md` for details

### Tailscale (Secure Network Access)

Access your container from anywhere via Tailscale's private network. **Built-in** - no sidecar container needed!

```bash
# Get auth key from: https://login.tailscale.com/admin/settings/keys
# Add to .env: TS_AUTHKEY=tskey-auth-xxxxx...

# Simply start the container - Tailscale starts automatically
docker-compose up -d

# Or use convenience targets
make up-tailscale          # Just Tailscale
make up-tailscale-web      # Tailscale + web terminal
```

**Perfect for:**
- 📱 Phone/tablet access from anywhere
- 👥 Team sharing and collaboration
- 🏠 Access from home or remote locations
- 🔒 Secure, zero-config VPN alternative
- ⚡ Built-in userspace networking (no special privileges)

Access from any device on your Tailscale network:
```bash
# Web terminal (if enabled)
http://claude-yolo:7681

# Direct service access
curl http://claude-yolo:8000
```

See `tailscale/README.md` for complete setup guide.

### OpenVPN (Corporate VPN Access)

Connect to your corporate VPN automatically on container startup. **Built-in** - no sidecar needed!

```bash
# Place your .ovpn file in openvpn/ directory
cp ~/company-vpn.ovpn ./openvpn/

# Configure in .env
OPENVPN_CONFIG=company-vpn.ovpn
# Optional: Add credentials if needed
OPENVPN_AUTH_USER=your-username
OPENVPN_AUTH_PASS=your-password

# Start container - OpenVPN connects automatically
docker-compose up -d

# Check VPN status
make openvpn-status
```

**Perfect for:**
- 🏢 Corporate development environments
- 🔐 Accessing internal APIs and databases
- 📊 Working with company resources
- 🌐 Testing behind corporate firewalls
- ⚙️ Supports certificate and password auth

**Benefits:**
- Auto-connects on startup
- Access internal company resources
- Works with any OpenVPN-compatible VPN
- Secure credential handling

See `openvpn/README.md` for detailed setup guide.

### Cloudflare Tunnel (Public Internet Access)

Expose your container securely to the public internet via Cloudflare's global network. **Built-in** - no port forwarding needed!

```bash
# Create tunnel at: https://one.dash.cloudflare.com/ → Access → Tunnels
# Copy the tunnel token

# Configure in .env
CLOUDFLARED_TUNNEL_TOKEN=eyJhIjoiY2xhdWRlLXlvbG8tZGVtbyIsInMi...

# Start container - Cloudflared connects automatically
docker-compose up -d

# Or use convenience targets
make up-cloudflared          # Just Cloudflared
make up-cloudflared-web      # Cloudflared + web terminal (public access!)
```

**Perfect for:**
- 🎯 Sales demos with instant public URLs
- 🤝 Customer access (no VPN client needed)
- 🌍 Public web terminal from anywhere
- 📡 Webhook/API testing with real public endpoints
- 🔒 Zero-trust with Cloudflare Access SSO

**Benefits:**
- No client software needed (just browser)
- Free SSL certificates & DDoS protection
- Works through any firewall
- Optional enterprise SSO (Google/GitHub/etc)
- Custom domains supported

Access via your configured public hostname:
```bash
# Configure in Cloudflare dashboard
https://demo.yourdomain.com
```

See `cloudflared/README.md` for complete setup guide with security best practices.

## Running Multiple Network Services

You can run Tailscale, OpenVPN, and Cloudflare Tunnel simultaneously, but be aware of potential conflicts:

**✅ Safe Combinations:**
- **Tailscale + Cloudflared** - No conflicts. Personal/team access + public demos.
- **OpenVPN (split-tunnel) + Cloudflared** - Works great. Corporate access + public exposure.
- **All three with split-tunnel VPN** - Best flexibility. Ensure OpenVPN config doesn't have `redirect-gateway`.

**⚠️ Potential Issues:**
- **OpenVPN full-tunnel + Tailscale/Cloudflared** - Full-tunnel VPN routes ALL traffic through corporate network, potentially breaking Tailscale and Cloudflared connections.
- **DNS conflicts** - Multiple services may try to control DNS. Keep `TS_ACCEPT_DNS=false` (default) to avoid issues.

**Detection:** Check your `.ovpn` file for `redirect-gateway def1` - this indicates full-tunnel mode that may cause conflicts.

**Troubleshooting:** All services log to `/logs/` - check `tailscale.log`, `openvpn.log`, and `cloudflared.log` if services fail to connect.

See individual service READMEs in `tailscale/`, `openvpn/`, and `cloudflared/` directories for detailed configuration.

## What's Included

**Development Tools:**
- **Claude Code:** Latest stable, bypassPermissions mode enabled
- **Python:** uv, ruff, mypy, pytest, bandit, pre-commit
- **Git:** git, GitHub CLI (gh)

**Cloud & Infrastructure:**
- **Cloud CLIs:** AWS CLI, Azure CLI (az), Google Cloud (gcloud)
- **Kubernetes:** kubectl, helm, k9s (terminal UI)
- **IaC:** Terraform
- **Containers:** Docker CLI, docker-compose

**Databases:**
- PostgreSQL client (psql)
- MySQL client (mysql)
- Redis client (redis-cli)
- MongoDB shell (mongosh)

**Utilities:**
- **YAML/JSON:** yq, jq
- **HTTP:** httpie, curl
- **Text:** vim, nano, ripgrep
- **Terminal:** tmux, htop

**Security & Safety Features:**
- **Secrets scanning:** gitleaks, detect-secrets (on every commit)
- **Security scanners:** trivy (containers/IaC), tfsec (Terraform)
- **Git hooks:** Force push prevention, large file detection
- **Code quality:** Ruff, mypy, pre-commit framework
- **Logging:** Comprehensive audit trails

## Documentation

- **CLAUDE.md** - Comprehensive guide for Claude Code
- **proxy/README.md** - Proxy and logging details
- **webterminal/README.md** - Web terminal and remote access setup
- **tailscale/README.md** - Tailscale integration and remote networking
- **openvpn/README.md** - OpenVPN client setup for corporate VPN access
- **.env.example** - Configuration options

## Target Users

This environment is designed for:
- Sales engineers demoing capabilities
- Forward-deployed engineers in customer environments
- CTOs and leadership experimenting with AI
- Anyone wanting maximum safety with maximum capability

## Why "YOLO Mode"?

YOLO = "You Only Live Once" - maximum autonomy for Claude Code.

But unlike true YOLO, this environment protects you:
- Container isolation limits blast radius
- Safety hooks prevent common mistakes
- Logs provide transparency
- Designed for users who may be disconnected from architecture details

## Architecture

```
┌─────────────────────────────────────┐
│  Host Machine (Protected)           │
│  ┌───────────────────────────────┐  │
│  │  Docker Container             │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  Claude Code (YOLO)     │  │  │
│  │  │  + Full Tooling         │  │  │
│  │  └─────────────────────────┘  │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  Safety Layer           │  │  │
│  │  │  - Secrets scanning     │  │  │
│  │  │  - Git hooks            │  │  │
│  │  │  - Logging              │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
│         ↕️ Logs & Workspace          │
└─────────────────────────────────────┘
```

## Contributing

This project balances maximum capability with maximum safety. When contributing:
- Consider inexperienced users who may not understand architecture
- Add logging for transparency
- Test safety features thoroughly
- Update documentation

## License

[Your license here]
