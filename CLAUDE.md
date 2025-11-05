# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project Overview

Docker-based Claude Code environment with safety features (secrets scanning, git hooks, command logging). Designed to protect both the host machine AND inexperienced users (sales engineers, FDEs, CTOs) from well-intentioned but potentially dangerous actions, while giving Claude Code maximum autonomy.

## Available Tools

**Core:** git, gh, jq, ripgrep (rg), vim, nano, tmux, htop
**Cloud:** aws, az, gcloud
**Kubernetes:** kubectl, helm, k9s, docker, docker-compose
**IaC:** terraform, tfsec
**Databases:** psql, mysql, redis-cli, mongosh
**Python:** uv (primary package manager), ruff, mypy, pytest, bandit, pre-commit
**Security:** gitleaks, detect-secrets, trivy
**Networking:** tailscale, openvpn, cloudflared, ttyd
**Utilities:** yq, httpie (http), curl, wget
**Build:** make, cmake, gcc/g++, Node.js 20

## File Structure

```
claude-yolo/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── Makefile
├── config/
│   ├── init.sh
│   ├── .pre-commit-config.yaml
│   ├── gitignore.template
│   ├── .claude/settings.local.json
│   └── git/hooks/ (pre-commit, pre-push)
├── scripts/
│   └── setup-project-safety.sh
├── proxy/
├── webterminal/
├── tailscale/
├── openvpn/
├── cloudflared/
└── logs/ (commands, safety, git, claude, proxy, tailscale.log, openvpn.log, cloudflared.log)
```

## Safety Constraints

**Container Isolation:**
- Runs as non-root user (developer, UID 1001)
- Resource limits: 2 CPU cores, 4GB RAM (configurable via `.env`)
- Network isolation via Docker bridge
- No Docker-in-Docker access

**Git Safety Hooks:**
- Pre-commit: Scans for secrets (gitleaks, detect-secrets), large files, sensitive patterns
- Pre-push: Prevents force push to main/master, warns on direct pushes
- Auto-configured via `core.hooksPath`

**Pre-commit Framework:**
- Secrets detection (gitleaks, detect-secrets)
- Python linting and formatting (ruff)
- Security scanning (bandit)
- File safety checks (large files, merge conflicts)

**Logging:**
- `/logs/commands/` - All shell commands with timestamps
- `/logs/claude/` - Claude Code session logs
- `/logs/git/` - Git operations
- `/logs/safety/` - Safety check results
- All logs shared with host via volume mount

**Claude Code Mode:**
- BypassPermissions mode enabled by default (`config/.claude/settings.local.json`)
- True YOLO mode - autonomous operation without permission prompts
- Safety provided by container isolation and hooks

## Networking Modes

The container supports two networking modes in `docker-compose.yml`. **Claude should recommend the appropriate mode based on user needs:**

### Mode 1: Bridge Networking (Default)
- **When to recommend:** Multi-container setups (databases, Redis, microservices)
- **Pros:** Docker DNS, network isolation, can join custom networks
- **Cons:** MCP OAuth callbacks won't work (requires manual port forwarding)
- **Config:** Uses `networks: - claude-network` (default in docker-compose.yml)

### Mode 2: Host Networking (For MCP OAuth)
- **When to recommend:** Single-container setup + user needs MCP server authentication (Atlassian, GitHub MCP servers)
- **Pros:** All ports accessible, MCP OAuth works seamlessly, zero overhead
- **Cons:** Cannot join Docker networks, no service discovery, multi-container setups won't work
- **Config:** Uncomment `network_mode: "host"` and comment out `networks:` in docker-compose.yml

### MCP OAuth Technical Background
Claude Code uses random ephemeral ports (49152-65535) for OAuth callbacks. Exposing this full range causes:
- Container startup hangs (hours) or complete failure
- 16GB+ RAM consumption
- Docker creates 16,384 iptables rules or docker-proxy processes

**Decision tree for users:**
- Planning to add databases/microservices? → Bridge mode (default)
- Need MCP OAuth + single container only? → Host mode
- Unsure? → Start with bridge mode (default)

See [GitHub Issue #2527](https://github.com/anthropics/claude-code/issues/2527) for Claude Code's OAuth port limitation and [Docker Issue #14288](https://github.com/moby/moby/issues/14288) for port range performance issues.

## File Boundaries

**Safe to edit:** `/workspace/*`, `/config/*`, `/scripts/*`, `Dockerfile`, `docker-compose.yml`, `.env`
**Read-only:** `/opt/config-templates/*`, `/logs/*` (view only)
**Never touch:** System directories, volume mount points

## Volume Mounts

- `/home/developer` - Named volume `claude-home` (persists config, git setup)
- `/workspace` - Host workspace directory (configurable via `HOST_WORKSPACE`)
- `/logs` - Shared logs directory (configurable via `HOST_LOGS`)
- `/mnt/host-gitconfig` - Optional mount for host git config

## Common Commands

```bash
# Set up safety features for a new project
/home/developer/scripts/setup-project-safety.sh /workspace/my-project

# View logs
tail -f /logs/safety/checks.log
tail -f /logs/git/operations.log

# Python projects (use uv as primary package manager)
uv init .
uv add <package>
```

## Development Approach

When working in this repository:

1. **Infrastructure Focus**: Changes typically involve Dockerfile, docker-compose, or shell scripts
2. **Safety First**: Every new capability should consider security implications
3. **User Protection**: Target users may be inexperienced - protect them from foot-guns
4. **Balance**: Maximum Claude Code autonomy within safety constraints
5. **Logging**: Ensure new features log appropriately for transparency
6. **Documentation**: Keep CLAUDE.md and README.md updated

IMPORTANT: This environment is designed for users who may be disconnected from architecture details. Always prioritize safety and transparency.

## Target Users

Sales Engineers (demoing safely), Forward-Deployed Engineers (customer environments), CTOs/Leadership (experimenting with Claude Code), Anyone wanting maximum autonomy with maximum safety.
