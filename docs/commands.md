# CLI Commands Reference

Complete reference for all `claude-yolo` commands.

## Global Options

```bash
claude-yolo --help          # Show help
claude-yolo --version       # Show version
```

---

## Project Lifecycle

### `init`

Initialize claude-yolo in the current directory.

```bash
claude-yolo init [OPTIONS]
```

**Options:**
- `--minimal` - Skip VPN/proxy configurations (faster, simpler setup)
- `--force` - Overwrite existing `.claude-yolo` directory without prompting

**Examples:**
```bash
# Standard initialization
claude-yolo init

# Minimal setup (no VPN configs)
claude-yolo init --minimal

# Force reinitialize
claude-yolo init --force
```

**What it creates:**
- `.claude-yolo/` - Docker configuration directory
- `logs/` - Log directories (commands, claude, git, safety)
- `.env` - Environment configuration file
- Updates `.gitignore` with claude-yolo entries

---

### `checkout`

Clone a repository and optionally initialize claude-yolo.

```bash
claude-yolo checkout REPO [OPTIONS]
```

**Arguments:**
- `REPO` - Repository URL or GitHub shorthand (`user/repo`)

**Options:**
- `--branch`, `-b` TEXT - Branch to checkout
- `--depth` INTEGER - Shallow clone depth
- `--force`, `-f` - Clone even if directory exists
- `--no-interactive` - Skip interactive prompts
- `--auto-start` - Auto-init, build, and start

**Examples:**
```bash
# GitHub shorthand
claude-yolo checkout anthropics/claude-yolo

# Full URL
claude-yolo checkout https://github.com/user/repo.git

# Specific branch
claude-yolo checkout user/repo --branch develop

# Shallow clone (faster)
claude-yolo checkout user/repo --depth 1

# Complete automated setup
claude-yolo checkout user/repo --auto-start
```

---

## Container Management

### `build`

Build the Docker image.

```bash
claude-yolo build [OPTIONS]
```

**Options:**
- `--no-cache` - Build without using cache (clean build)
- `--no-pull` - Don't pull base image updates

**Examples:**
```bash
# Standard build
claude-yolo build

# Clean build (no cache)
claude-yolo build --no-cache

# Build without pulling updates
claude-yolo build --no-pull
```

**Hooks:**
- Runs `pre-build.sh` hook before building
- Runs `post-build.sh` hook after building

---

### `run`

Start the container.

```bash
claude-yolo run [OPTIONS]
```

**Options:**
- `--detach`, `-d` - Run in background
- `--no-build` - Skip building image first

**Examples:**
```bash
# Start interactively (attached)
claude-yolo run

# Start in background
claude-yolo run --detach

# Start without rebuilding
claude-yolo run --no-build
```

**Hooks:**
- Runs `pre-start.sh` hook before starting container

---

### `shell`

Open an interactive shell in the running container. Uses persistent tmux sessions so you can disconnect and reconnect without losing your work.

```bash
claude-yolo shell
```

**Examples:**
```bash
# Open persistent tmux shell
claude-yolo shell

# Then inside container:
# - Run your development commands
# - Test your application
# - Use all installed tools
# - Disconnect with Ctrl+B then D
# - Reconnect anytime with claude-yolo shell
```

---

### `stop`

Stop the running container.

```bash
claude-yolo stop
```

**Examples:**
```bash
claude-yolo stop
```

---

### `restart`

Restart the container.

```bash
claude-yolo restart [OPTIONS]
```

**Options:**
- `--build` - Rebuild image before restarting

**Examples:**
```bash
# Simple restart
claude-yolo restart

# Rebuild and restart
claude-yolo restart --build
```

---

### `clean`

Remove containers and optionally volumes.

```bash
claude-yolo clean [OPTIONS]
```

**Options:**
- `--volumes` - Also remove volumes (deletes all data!)
- `--force`, `-f` - Don't ask for confirmation

**Examples:**
```bash
# Remove containers only
claude-yolo clean

# Remove containers and volumes
claude-yolo clean --volumes

# Force clean without confirmation
claude-yolo clean --volumes --force
```

**Warning:** Using `--volumes` will delete all data in Docker volumes, including databases.

---

## Monitoring & Debugging

### `status`

Show container status and resource usage.

```bash
claude-yolo status
```

**Shows:**
- Container running status
- Resource usage (CPU, memory)
- Enabled VPN/proxy features
- Web terminal URL and status (if enabled)
- Port mappings

**Examples:**
```bash
claude-yolo status
```

---

### `logs`

View container logs.

```bash
claude-yolo logs [TYPE] [OPTIONS]
```

**Arguments:**
- `TYPE` - Log type: `commands`, `claude`, `git`, `safety`, or empty for all

**Options:**
- `--follow`, `-f` - Follow log output (like `tail -f`)
- `--tail` INTEGER - Number of lines to show (default: 100)

**Examples:**
```bash
# View all logs
claude-yolo logs

# View specific log type
claude-yolo logs commands
claude-yolo logs safety

# Follow logs in real-time
claude-yolo logs --follow

# Show last 50 lines
claude-yolo logs --tail 50

# Follow specific log type
claude-yolo logs claude --follow
```

**Log Types:**
- `commands` - All shell commands executed (directory)
- `claude` - Claude Code session logs (directory)
- `git` - Git operations (directory)
- `safety` - Security scans and safety checks (directory)
- `proxy` - Proxy logs (single file, if proxy enabled)
- `tailscale` - Tailscale VPN logs (single file, if enabled)
- `openvpn` - OpenVPN logs (single file, if enabled)
- `cloudflared` - Cloudflare Tunnel logs (single file, if enabled)

---

### `doctor`

Run diagnostics to check system requirements.

```bash
claude-yolo doctor
```

**Checks:**
- Docker installed and running
- docker-compose available
- Git installed
- Project initialized
- Required files present
- Port availability

**Examples:**
```bash
claude-yolo doctor
```

---

## VPN & Remote Access

### `vpn`

Show VPN configuration status.

```bash
claude-yolo vpn [COMMAND]
```

**Commands:**
- `status` - Show current VPN configuration

**Examples:**
```bash
# Show VPN status
claude-yolo vpn status
```

**Shows:**
- Tailscale configuration
- OpenVPN configuration
- Cloudflare Tunnel configuration
- Enabled/disabled status for each

**Notes:**
- VPN management is primarily done through `.env` configuration. See [VPN Setup Guide](vpn-setup.md).
- Connection status checking is not yet fully implemented and may show "Unknown" for active connections.

---

## Updates & Maintenance

### `update`

Update template files (coming soon).

```bash
claude-yolo update [OPTIONS]
```

**Status:** This command is planned for a future release.

**Planned features:**
- Update Docker and configuration files to latest templates
- Preserve user customizations
- Show diff before applying
- Backup old configuration

---

## Environment Variables

Key environment variables (edit in `.env`):

### Container Configuration
```bash
CONTAINER_NAME=claude-yolo          # Container name
CONTAINER_CPU_LIMIT=2.0             # CPU limit
CONTAINER_MEMORY_LIMIT=4G           # Memory limit
APP_PORT=8000                       # Application port
```

### Logging
```bash
CLAUDE_LOG_LEVEL=info               # Log level (debug, info, warn, error)
```

### VPN Configuration
```bash
# Tailscale
TS_AUTHKEY=tskey-...                # Tailscale auth key
TS_HOSTNAME=claude-yolo             # Hostname on Tailscale network

# OpenVPN
OPENVPN_CONFIG=client.ovpn          # OpenVPN config file
OPENVPN_AUTH_USER=username          # VPN username (optional)
OPENVPN_AUTH_PASS=password          # VPN password (optional)

# Cloudflare Tunnel
CLOUDFLARED_TUNNEL_TOKEN=ey...      # Tunnel token
```

### Host Paths
```bash
HOST_WORKSPACE=./workspace          # Host workspace directory
HOST_LOGS=./logs                    # Host logs directory
```

---

## Exit Codes

- `0` - Success
- `1` - General error
- `>1` - Command-specific error (matches subprocess exit code)

---

## Tips & Tricks

**Chain Commands:**
```bash
claude-yolo build && claude-yolo run --detach && claude-yolo shell
```

**Watch Logs:**
```bash
# Terminal 1
claude-yolo run

# Terminal 2
claude-yolo logs --follow
```

**Quick Rebuild:**
```bash
claude-yolo restart --build
```

**Check Before Building:**
```bash
claude-yolo doctor
```

**Emergency Clean:**
```bash
claude-yolo clean --volumes --force
docker system prune -af
```

---

## See Also

- [Quick Start Guide](quickstart.md)
- [Customization Guide](customization.md)
- [VPN Setup](vpn-setup.md)
- [Troubleshooting](troubleshooting.md)
