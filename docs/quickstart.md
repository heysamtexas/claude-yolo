# Quick Start Guide

Get up and running with claude-yolo in 5 minutes.

## Installation

Choose your preferred installation method:

### Using uv (Recommended - Fastest)
```bash
uv tool install claude-yolo
```

### Using pipx (Isolated Environment)
```bash
pipx install claude-yolo
```

### Using pip
```bash
pip install claude-yolo
```

## Prerequisites

- **Docker**: claude-yolo requires Docker to be installed and running
- **Docker Compose**: Should be installed with Docker Desktop, or install separately
- **Git**: For repository checkout features

Verify your installation:
```bash
docker --version
docker-compose --version
git --version
```

## Your First Project

### Option 1: Initialize in Existing Project

```bash
# Navigate to your project
cd my-project

# Initialize claude-yolo
claude-yolo init

# Review configuration
vim .env

# Build the Docker environment
claude-yolo build

# Start the container
claude-yolo run

# Open a shell in the container
claude-yolo shell
```

### Option 2: Checkout and Auto-Setup

Clone a repository and set up claude-yolo in one command:

```bash
# GitHub shorthand
claude-yolo checkout user/repo --auto-start

# Or with full URL
claude-yolo checkout https://github.com/user/repo --auto-start
```

This will:
1. Clone the repository
2. Initialize claude-yolo
3. Build the Docker image
4. Start the container

## What Gets Created

After `claude-yolo init`, your project will have:

```
my-project/
├── .claude-yolo/           # Docker configuration (you own this!)
│   ├── Dockerfile          # Customize as needed
│   ├── docker-compose.yml  # Container orchestration
│   ├── config/             # Git hooks, pre-commit setup
│   ├── scripts/            # Safety and setup scripts
│   └── hooks/              # Customization hooks
├── logs/                   # Runtime logs (transparent operation)
│   ├── commands/           # All shell commands
│   ├── claude/             # Claude Code logs
│   ├── git/                # Git operations
│   └── safety/             # Security scans
└── .env                    # Your configuration
```

## Basic Workflow

```bash
# Check system requirements
claude-yolo doctor

# Build Docker image
claude-yolo build

# Start container (detached)
claude-yolo run

# Open interactive shell
claude-yolo shell

# View logs
claude-yolo logs

# Check status
claude-yolo status

# Stop container
claude-yolo stop

# Clean up everything
claude-yolo clean
```

## Key Features Out of the Box

### Safety Features
- **Secrets scanning** with gitleaks and detect-secrets
- **Git hooks** prevent force pushes and large files
- **Container isolation** protects your host machine
- **Comprehensive logging** for transparency

### Development Tools
- Python: uv, ruff, mypy, pytest
- Cloud CLIs: AWS, Azure, Google Cloud
- Kubernetes: kubectl, helm, k9s
- Infrastructure: Terraform, Docker, docker-compose
- Databases: PostgreSQL, MySQL, Redis, MongoDB clients

### Remote Access (Optional)
- **Tailscale**: Secure remote access from anywhere
- **OpenVPN**: Corporate VPN connectivity
- **Cloudflare Tunnel**: Expose to internet securely
- **Web Terminal**: Browser-based access

## Configuration

Edit `.env` to customize your setup:

```bash
# Container resources
CONTAINER_CPU_LIMIT=2.0
CONTAINER_MEMORY_LIMIT=4G

# Application port
APP_PORT=8000

# Enable VPN (optional)
# TS_AUTHKEY=tskey-...
# OPENVPN_CONFIG=client.ovpn
# CLOUDFLARED_TUNNEL_TOKEN=ey...
```

## Next Steps

- **[Commands Reference](commands.md)** - Complete CLI documentation
- **[Customization Guide](customization.md)** - Editing Dockerfile and hooks
- **[VPN Setup](vpn-setup.md)** - Remote access configuration
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## Quick Tips

**Minimal Installation** (skip VPN configs):
```bash
claude-yolo init --minimal
```

**Rebuild After Changes**:
```bash
claude-yolo restart --build
```

**View Specific Logs**:
```bash
claude-yolo logs commands
claude-yolo logs safety
```

**Check Configuration**:
```bash
cat .env
```

## Getting Help

```bash
# Show all commands
claude-yolo --help

# Show command-specific help
claude-yolo init --help
claude-yolo checkout --help
```

## Common First-Time Issues

1. **"Docker daemon not running"**
   - Start Docker Desktop
   - Or start Docker service: `sudo systemctl start docker`

2. **"Port already in use"**
   - Edit `.env` and change `APP_PORT` to a different port
   - Or stop the conflicting service

3. **"Permission denied"**
   - Ensure Docker is installed and your user is in the `docker` group
   - On Linux: `sudo usermod -aG docker $USER` (then log out and back in)

For more issues, see [Troubleshooting](troubleshooting.md).
