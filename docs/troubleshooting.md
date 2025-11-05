# Troubleshooting Guide

Solutions to common issues you may encounter with claude-yolo.

## Quick Diagnostics

**Always start here:**
```bash
claude-yolo doctor
```

This checks:
- Docker installation and daemon status
- docker-compose availability
- Git installation
- Project initialization
- Required files
- Port availability

---

## Installation Issues

### "Command not found: claude-yolo"

**Problem:** CLI not in PATH after installation.

**Solutions:**

```bash
# If installed with pipx
pipx ensurepath
# Then restart your shell

# If installed with pip
pip install --user claude-yolo
# Add ~/.local/bin to PATH

# If installed with uv
uv tool install claude-yolo
# uv handles PATH automatically

# Verify installation
which claude-yolo
claude-yolo --version
```

### "No module named 'claude_yolo'"

**Problem:** Package not properly installed.

**Solution:**
```bash
# Reinstall
pipx uninstall claude-yolo
pipx install claude-yolo

# Or with pip
pip uninstall claude-yolo
pip install claude-yolo

# Verify
python -c "import claude_yolo; print(claude_yolo.__version__)"
```

---

## Docker Issues

### "Docker daemon is not running"

**Problem:** Docker Desktop or Docker service isn't started.

**Solutions:**

**macOS/Windows:**
```bash
# Start Docker Desktop application
open -a Docker  # macOS

# Wait for Docker to start (30-60 seconds)
# Check status
docker info
```

**Linux:**
```bash
# Start Docker service
sudo systemctl start docker

# Enable on boot
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

### "Permission denied" when running docker commands

**Problem:** User not in docker group (Linux).

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in for changes to take effect
# Or use: newgrp docker

# Verify
docker ps
```

### "Cannot connect to Docker daemon"

**Problem:** Docker socket not accessible.

**Solutions:**
```bash
# Check Docker is running
docker info

# On Linux, check socket permissions
ls -l /var/run/docker.sock

# If needed, fix permissions
sudo chmod 666 /var/run/docker.sock

# Or restart Docker
sudo systemctl restart docker
```

### "Error response from daemon: conflict"

**Problem:** Container or resource name already in use.

**Solution:**
```bash
# Stop and remove existing container
docker ps -a | grep claude-yolo
docker rm -f <container-id>

# Or use clean command
claude-yolo clean --force

# Then try again
claude-yolo run
```

---

## Build Issues

### Build fails with "No space left on device"

**Problem:** Docker ran out of disk space.

**Solutions:**
```bash
# Clean up Docker resources
docker system prune -af
docker volume prune -f

# Check available space
docker system df

# On macOS, increase Docker Desktop disk size
# Docker Desktop → Settings → Resources → Disk image size
```

### "Unable to find image" or "manifest unknown"

**Problem:** Base image not found or registry issue.

**Solutions:**
```bash
# Pull base image manually
docker pull ubuntu:24.04

# Check Docker Hub status
# https://status.docker.com/

# If behind a proxy, configure Docker proxy
# Docker Desktop → Settings → Resources → Proxies
```

### Build is extremely slow

**Problem:** Downloading packages, no cache, or resource limits.

**Solutions:**
```bash
# Use build cache (default)
claude-yolo build

# Increase resources (Docker Desktop)
# Settings → Resources → CPUs: 4+, Memory: 8GB+

# On slow network, increase timeout in Dockerfile
# RUN apt-get update ... (may take 10-20 minutes first time)

# Check internet connectivity
ping -c 3 archive.ubuntu.com
```

### "Package not found" during build

**Problem:** Package name incorrect or repository not available.

**Solutions:**
```bash
# Update package lists in Dockerfile
RUN apt-get update && apt-get install -y package-name

# For Python packages
RUN uv pip install --system package-name

# For Node packages
RUN npm install -g package-name

# Check package exists
# https://packages.ubuntu.com/
```

---

## Runtime Issues

### Container exits immediately after starting

**Problem:** Error in startup scripts or Dockerfile.

**Solutions:**
```bash
# Check logs
claude-yolo logs
docker logs claude-yolo

# Try interactive mode
claude-yolo run  # Without --detach

# Check specific logs
claude-yolo logs claude
claude-yolo logs commands

# Debug by running shell directly
docker run -it --entrypoint /bin/bash claude-yolo
```

### "Port already allocated" error

**Problem:** Port is in use by another application.

**Solutions:**
```bash
# Find what's using the port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Option 1: Stop the conflicting service
kill <PID>

# Option 2: Change port in .env
echo "APP_PORT=8001" >> .env
claude-yolo restart

# Option 3: Use different port in docker-compose.yml
# Change: - "8000:8000" to - "8001:8000"
```

### "Container is not running"

**Problem:** Container stopped or never started.

**Solutions:**
```bash
# Check status
claude-yolo status
docker ps -a | grep claude-yolo

# Check logs for why it stopped
claude-yolo logs

# Restart
claude-yolo restart

# If keeps stopping, try interactive mode
claude-yolo run  # See errors in real-time
```

### Cannot access application on localhost:8000

**Problem:** Port mapping or application not listening.

**Solutions:**
```bash
# Verify container is running
claude-yolo status

# Check port mapping
docker ps | grep claude-yolo

# Test from inside container
claude-yolo shell
curl http://localhost:8000

# Check firewall
sudo ufw status  # Linux
# Ensure port 8000 is allowed

# Check application is listening
claude-yolo shell
netstat -tlnp | grep 8000
```

---

## Initialization Issues

### "Already initialized" when running init

**Problem:** `.claude-yolo/` directory already exists.

**Solutions:**
```bash
# Option 1: Use force flag
claude-yolo init --force

# Option 2: Remove and re-init
rm -rf .claude-yolo
claude-yolo init

# Option 3: Just rebuild
claude-yolo build --no-cache
```

### "Permission denied" creating files

**Problem:** Insufficient permissions in current directory.

**Solutions:**
```bash
# Check directory permissions
ls -la

# Ensure you own the directory
sudo chown -R $USER:$USER .

# Or initialize in a directory you own
cd ~/projects/my-project
claude-yolo init
```

### Missing files after init

**Problem:** Init partially failed or templates not found.

**Solutions:**
```bash
# Check templates exist in package
python -c "from claude_yolo.init import get_templates_dir; print(get_templates_dir())"

# Reinstall package
pipx reinstall claude-yolo

# Run init again
claude-yolo init --force

# Verify structure
ls -la .claude-yolo/
ls -la logs/
```

---

## Network Issues

### Cannot reach external services from container

**Problem:** Network configuration or DNS issues.

**Solutions:**
```bash
# Test DNS from inside container
claude-yolo shell
ping -c 3 google.com
nslookup github.com

# Check Docker network
docker network ls
docker network inspect bridge

# Try custom DNS in docker-compose.yml
dns:
  - 8.8.8.8
  - 8.8.4.4

# Restart with new config
claude-yolo restart
```

### VPN prevents Docker networking

**Problem:** VPN interfering with Docker network.

**Solutions:**
```bash
# Add Docker subnet to VPN split tunnel
# Docker default: 172.17.0.0/16

# Or disconnect VPN temporarily
# Then reconnect after starting container

# Configure VPN to exclude Docker networks
# (See VPN client documentation)
```

---

## Git Issues

### Git hooks not working

**Problem:** Hooks not executable or not configured.

**Solutions:**
```bash
# Check hooks are executable
ls -la .claude-yolo/config/git/hooks/

# Make executable if needed
chmod +x .claude-yolo/config/git/hooks/*

# Verify git config
git config core.hooksPath
# Should be: .claude-yolo/config/git/hooks

# Set manually if needed
git config core.hooksPath .claude-yolo/config/git/hooks
```

### "Command not found" in git hooks

**Problem:** Tools not in PATH when hook runs.

**Solutions:**
```bash
# Hooks run outside container, need tools on host
# Install required tools:
brew install gitleaks  # macOS
apt-get install gitleaks  # Linux

# Or disable problematic checks
# Edit .claude-yolo/config/git/hooks/pre-commit
# Comment out failing commands
```

---

## VPN Issues

### Tailscale: "Failed to authenticate"

**Solutions:**
```bash
# Check auth key is valid
echo $TS_AUTHKEY

# Generate new key: https://login.tailscale.com/admin/settings/keys
# Update .env with new key

# Check for typos in .env
cat .env | grep TS_AUTHKEY

# Restart container
claude-yolo restart
```

### OpenVPN: "Cannot open TUN/TAP device"

**Problem:** Container lacks privileges for VPN.

**Solutions:**
```bash
# Add capabilities in docker-compose.yml
cap_add:
  - NET_ADMIN
devices:
  - /dev/net/tun

# Or run in privileged mode (less secure)
privileged: true

# Restart
claude-yolo restart --build
```

### Cloudflare: "Unable to reach origin"

**Solutions:**
```bash
# Verify application is running
claude-yolo shell
curl http://localhost:8000

# Check tunnel token is correct
echo $CLOUDFLARED_TUNNEL_TOKEN

# Check tunnel status in dashboard
# https://one.dash.cloudflare.com/ → Tunnels

# View cloudflared logs
claude-yolo logs | grep cloudflared
```

---

## Resource Issues

### Container uses too much memory

**Problem:** Application memory leak or limits too high.

**Solutions:**
```bash
# Check current usage
docker stats claude-yolo

# Reduce limits in .env
CONTAINER_MEMORY_LIMIT=2G  # Reduce from 4G
CONTAINER_MEMORY_RESERVATION=512M

# Restart
claude-yolo restart

# Monitor over time
watch -n 5 'docker stats --no-stream claude-yolo'
```

### Container uses too much CPU

**Solutions:**
```bash
# Check what's using CPU
claude-yolo shell
top

# Reduce CPU limit in .env
CONTAINER_CPU_LIMIT=1.0  # Reduce from 2.0

# Check for runaway processes
ps aux | sort -rk 3,3 | head -10

# Restart
claude-yolo restart
```

### Disk space issues

**Solutions:**
```bash
# Check Docker disk usage
docker system df

# Clean up old images and containers
docker system prune -a
docker volume prune

# Check volumes
docker volume ls
claude-yolo clean --volumes --force

# On macOS, increase Docker Desktop disk size
# Settings → Resources → Disk image size
```

---

## Performance Issues

### Slow file operations (especially macOS)

**Problem:** Docker volume performance on macOS.

**Solutions:**
```bash
# Use :delegated for better performance
# In docker-compose.yml:
volumes:
  - ${HOST_WORKSPACE:-..}:/workspace:delegated

# Or use named volumes for node_modules
volumes:
  - ${HOST_WORKSPACE:-..}:/workspace
  - node_modules:/workspace/node_modules

# Consider using Docker Desktop with VirtioFS
# Settings → Experimental Features → VirtioFS
```

### Container startup is slow

**Solutions:**
```bash
# Pre-build image
claude-yolo build

# Start in background
claude-yolo run --detach

# Reduce services if not needed
# Comment out in docker-compose.yml

# Check for network issues
# Slow DNS, VPN overhead, etc.
```

---

## Logs and Debugging

### Cannot find logs

**Solutions:**
```bash
# Check logs directory exists
ls -la logs/

# View all logs
claude-yolo logs

# View specific type
claude-yolo logs commands
claude-yolo logs claude
claude-yolo logs safety
claude-yolo logs git

# View Docker logs directly
docker logs claude-yolo

# Follow logs in real-time
claude-yolo logs --follow
```

### Logs directory empty

**Solutions:**
```bash
# Check directory structure
ls -la logs/*/

# Logs created on first write
# Run some commands first
claude-yolo shell

# Check permissions
ls -ld logs/
# Should be writable by your user
```

---

## macOS Specific Issues

### "Rosetta is required" on Apple Silicon

**Problem:** Need x86 emulation for some images.

**Solution:**
```bash
# Install Rosetta
softwareupdate --install-rosetta

# Restart Docker Desktop
```

### Slow performance on macOS

**Solutions:**
```bash
# Use VirtioFS (faster file sharing)
# Docker Desktop → Settings → Experimental → VirtioFS

# Increase Docker Desktop resources
# Settings → Resources → CPUs: 4+, Memory: 8GB+

# Use :delegated mount option
# See docker-compose.yml volumes section
```

---

## Linux Specific Issues

### SELinux prevents container access

**Problem:** SELinux blocking Docker operations.

**Solutions:**
```bash
# Add :Z flag to volumes in docker-compose.yml
volumes:
  - ${HOST_WORKSPACE:-..}:/workspace:Z

# Or temporarily disable SELinux (not recommended for production)
sudo setenforce 0

# Check SELinux status
getenforce
```

### AppArmor denials

**Solutions:**
```bash
# Check AppArmor logs
sudo dmesg | grep -i apparmor

# Add docker profile exception
sudo aa-complain /etc/apparmor.d/docker

# Restart Docker
sudo systemctl restart docker
```

---

## Windows Specific Issues

### WSL2 required but not installed

**Solutions:**
```bash
# Install WSL2
wsl --install

# Set WSL2 as default
wsl --set-default-version 2

# Restart Docker Desktop
```

### Path translation issues

**Problem:** Windows paths don't work in container.

**Solutions:**
```bash
# Use WSL2 paths
# Instead of: C:\Users\...
# Use: /mnt/c/Users/...

# Or use Windows paths with forward slashes
# /c/Users/... works in some contexts
```

---

## Getting More Help

### Enable Debug Mode

```bash
# Set in .env
CLAUDE_LOG_LEVEL=debug

# Restart
claude-yolo restart

# View verbose logs
claude-yolo logs --follow
```

### Collect Diagnostic Information

```bash
# Run diagnostics
claude-yolo doctor > diagnostics.txt

# System information
uname -a >> diagnostics.txt
docker version >> diagnostics.txt
docker info >> diagnostics.txt

# Container status
docker ps -a >> diagnostics.txt
docker inspect claude-yolo >> diagnostics.txt

# Logs
claude-yolo logs > logs.txt
```

### Report an Issue

When reporting issues, include:
1. Output of `claude-yolo doctor`
2. Output of `claude-yolo --version`
3. Your OS and version
4. Docker version: `docker --version`
5. Relevant logs: `claude-yolo logs`
6. What you were trying to do
7. What actually happened
8. Any error messages

**GitHub Issues:** https://github.com/anthropics/claude-yolo/issues

---

## Common Error Messages

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| "command not found: docker" | Docker not installed | Install Docker Desktop |
| "Cannot connect to Docker daemon" | Docker not running | Start Docker Desktop/service |
| "port is already allocated" | Port conflict | Change port or stop conflicting service |
| "no such file or directory" | Wrong directory or not initialized | Run `claude-yolo init` |
| "permission denied" | User permissions | Add user to docker group (Linux) |
| "manifest unknown" | Image not found | Check internet, Docker Hub status |
| "no space left on device" | Disk full | Run `docker system prune -af` |
| "container exits with code 137" | Out of memory | Increase memory limit |
| "TLS handshake timeout" | Network issue | Check firewall, proxy settings |

---

## Emergency Recovery

### Complete Reset

If nothing works, nuclear option:

```bash
# Stop all containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all images
docker rmi $(docker images -q)

# Remove all volumes
docker volume prune -f

# Remove all networks
docker network prune -f

# Full system prune
docker system prune -af --volumes

# Restart Docker
# macOS/Windows: Restart Docker Desktop
# Linux: sudo systemctl restart docker

# Reinitialize claude-yolo
cd your-project
rm -rf .claude-yolo logs .env
claude-yolo init
claude-yolo build
claude-yolo run
```

---

## See Also

- [Quick Start Guide](quickstart.md)
- [Commands Reference](commands.md)
- [Customization Guide](customization.md)
- [VPN Setup](vpn-setup.md)
