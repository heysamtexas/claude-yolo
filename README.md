# claude-yolo

> Claude Code YOLO mode - Docker-based development environment with safety features

A professional CLI tool that provides a secure, isolated Docker environment for Claude Code with maximum autonomy. It combines powerful development tools with built-in safety features including secrets scanning, git hooks, comprehensive logging, and VPN/proxy support.

Perfect for sales engineers, forward-deployed engineers, CTOs, and anyone who wants maximum autonomy with maximum safety.

## ✨ Features

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

## 🚀 Quick Start

### Installation

```bash
# Using uv (recommended, fastest)
uv tool install claude-yolo

# Using pipx (isolated environment)
pipx install claude-yolo

# Using pip (traditional)
pip install claude-yolo
```

### Start a New Project

**Option 1: Clone and auto-setup**
```bash
# Clone a repository and automatically initialize
claude-yolo checkout https://github.com/user/awesome-project
# Interactive prompts guide you through:
# → Initialize claude-yolo? [Y/n]
# → Build container? [Y/n]
# → Start container? [Y/n]

# Or non-interactive mode
claude-yolo checkout user/repo --auto-start
```

**Option 2: Initialize an existing project**
```bash
cd my-existing-project
claude-yolo init           # Set up claude-yolo infrastructure
claude-yolo build          # Build Docker image (5-10 min first time)
claude-yolo run            # Start container
claude-yolo shell          # Open shell
```

### Start Coding

```bash
# You're now in a safe, isolated environment!
# All your favorite tools are ready:

# Python projects (uv is primary package manager)
uv init my-app
cd my-app
uv add fastapi uvicorn

# Git operations are automatically safety-checked
git commit -m "Add feature"  # Scans for secrets, large files
git push  # Prevents force push to main/master

# View what Claude and your commands are doing
claude-yolo logs --type safety --follow
```

## 📖 CLI Commands

```bash
# Project Setup
claude-yolo init [--minimal]              # Initialize in current directory
claude-yolo checkout <repo> [options]     # Clone and setup repository

# Container Lifecycle
claude-yolo build [--no-cache]            # Build Docker image
claude-yolo run [--detach] [--mcp]        # Start container (--mcp for MCP OAuth)
claude-yolo shell                         # Open shell in container
claude-yolo stop                          # Stop container
claude-yolo restart [--build]             # Restart (optionally rebuild)
claude-yolo clean [--volumes]             # Remove containers/volumes

# Monitoring & Debugging
claude-yolo logs [--type TYPE] [--follow] # View logs
claude-yolo status                        # Show container status
claude-yolo doctor                        # Diagnose issues

# VPN & Network
claude-yolo vpn status                    # Check VPN status

# Maintenance
claude-yolo update                        # Update templates
claude-yolo version                       # Show version
```

### Checkout Command Examples

```bash
# Clone and auto-setup
claude-yolo checkout https://github.com/user/repo

# GitHub shorthand
claude-yolo checkout user/repo

# Specific branch with shallow clone
claude-yolo checkout user/repo --branch develop --depth 1

# Non-interactive CI/CD mode
claude-yolo checkout user/repo --no-interactive --auto-start
```

### Logs Command Examples

```bash
# View all recent logs
claude-yolo logs

# Follow specific log type
claude-yolo logs --type safety --follow
claude-yolo logs --type git --tail 50

# Available log types:
# commands, claude, git, safety, proxy, tailscale, openvpn, cloudflared
```

## 📁 Project Structure

When you run `claude-yolo init`, it creates:

```
my-project/
├── .claude-yolo/              # All infrastructure
│   ├── Dockerfile             # Customizable (edit freely!)
│   ├── docker-compose.yml     # Container config
│   ├── config/                # Git hooks, pre-commit
│   ├── scripts/               # Safety setup scripts
│   ├── tailscale/            # Tailscale configs
│   ├── openvpn/              # OpenVPN configs
│   ├── cloudflared/          # Cloudflared configs
│   ├── proxy/                # Proxy settings
│   └── hooks/                # Customization hooks
│       ├── pre-build.sh       # Before Docker build
│       ├── post-build.sh      # After Docker build
│       └── pre-start.sh       # Before container start
├── logs/                      # Runtime logs (auto-created)
│   ├── commands/             # All shell commands
│   ├── claude/               # Claude Code sessions
│   ├── git/                  # Git operations
│   ├── safety/               # Safety checks
│   ├── proxy.log
│   ├── tailscale.log
│   ├── openvpn.log
│   └── cloudflared.log
└── .env                       # Your configuration
```

## ⚙️ Configuration

Edit `.env` to customize:

```bash
# Container
CONTAINER_NAME=claude-yolo
CPU_LIMIT=2
MEMORY_LIMIT=4g

# Ports
APP_PORT=8000
WEB_TERMINAL_PORT=7681

# Features (set to true to enable)
ENABLE_TAILSCALE=false
ENABLE_OPENVPN=false
ENABLE_CLOUDFLARED=false
ENABLE_WEB_TERMINAL=true

# Logging
CLAUDE_LOG_LEVEL=info
```

### Networking Modes

Claude-yolo supports two networking modes. **Choose based on your use case:**

#### Mode 1: Bridge Networking (Default)

**Use this for:** Multi-container setups with databases, Redis, microservices, etc.

| Port | Purpose | Configurable |
|------|---------|--------------|
| `8000` | Application port (FastAPI, Flask, etc.) | ✅ via `APP_PORT` |
| `7681` | Web terminal (browser access) | ✅ via `WEBTERMINAL_PORT` |

**Pros:**
- ✅ Container-to-container communication via Docker DNS
- ✅ Network isolation between services
- ✅ Can join custom Docker networks
- ✅ Perfect for complex architectures

**Cons:**
- ❌ MCP OAuth callbacks won't work automatically (requires manual port forwarding)

#### Mode 2: Host Networking (For MCP OAuth)

**Use this for:** Single-container setup when you need MCP server authentication (Atlassian, GitHub, etc.)

To enable MCP OAuth mode:
```bash
# Simply add the --mcp flag when running
claude-yolo run --mcp

# Or run in background
claude-yolo run --mcp --detach
```

**What happens:**
- Container uses host networking instead of bridge
- All container ports automatically accessible on host
- MCP OAuth callbacks work on any random port

**Pros:**
- ✅ One simple flag - no manual configuration
- ✅ MCP OAuth callbacks work seamlessly
- ✅ Zero port mapping overhead
- ✅ Easy to switch back to bridge mode (run without `--mcp`)

**Cons:**
- ❌ Cannot join other Docker networks
- ❌ No Docker DNS for service discovery
- ❌ Not suitable for multi-container setups

**Example workflow:**
```bash
# Initialize project
claude-yolo init

# Run in MCP mode for OAuth
claude-yolo run --mcp

# Authenticate with MCP servers (Atlassian, GitHub, etc.)
# OAuth callbacks will work seamlessly

# Later, if you need bridge mode for multi-container
claude-yolo run  # Without --mcp flag
```

#### Why This Limitation Exists

Claude Code uses random ephemeral ports (49152-65535) for OAuth callbacks when authenticating with MCP servers. This is a technical limitation of Claude Code's OAuth implementation - the port cannot be predicted or configured.

Exposing the full ephemeral port range causes **severe performance issues**:
- Container startup hangs or takes hours
- Consumes 16GB+ RAM
- Docker creates 16,384 iptables rules or docker-proxy processes

**Technical details:**
- [Claude Code Issue #2527](https://github.com/anthropics/claude-code/issues/2527) - OAuth port selection
- [Docker Issue #14288](https://github.com/moby/moby/issues/14288) - Large port range performance

## 🔧 Customization

### Customize the Dockerfile

Edit `.claude-yolo/Dockerfile` - there's a dedicated user customization section:

```dockerfile
# >>> USER CUSTOMIZATION START >>>
# Add your custom tools, packages, configurations
RUN apt-get install -y postgresql-client-15
RUN uv pip install pandas numpy scikit-learn
# >>> USER CUSTOMIZATION END >>>
```

Then rebuild:
```bash
claude-yolo build
```

### Use Customization Hooks

```bash
# Pre-build: Generate configs, fetch secrets
vim .claude-yolo/hooks/pre-build.sh

# Post-build: Tag images, push to registry
vim .claude-yolo/hooks/post-build.sh

# Pre-start: Validate environment, check VPN
vim .claude-yolo/hooks/pre-start.sh
```

Hooks run automatically during `build` and `run`.

## Running Web Applications

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

## 📊 Viewing Logs

All activity is logged to `./logs/` (shared between host and container):

```bash
# Use the CLI (recommended)
claude-yolo logs                     # View all recent logs
claude-yolo logs --type safety -f   # Follow safety checks
claude-yolo logs --type git          # View git operations
claude-yolo logs --type commands     # View all commands

# Or directly on host
tail -f logs/safety/checks.log
tail -f logs/git/operations.log
```

**Log Types:**
- `commands/` - Every shell command executed (with timestamps)
- `claude/` - Claude Code session logs
- `git/` - All git operations
- `safety/` - Security scans and safety checks
- VPN logs: `tailscale.log`, `openvpn.log`, `cloudflared.log`

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
