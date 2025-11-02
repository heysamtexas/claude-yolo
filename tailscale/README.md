# Tailscale Integration

Access your Claude YOLO environment from anywhere on your private Tailscale network - phone, tablet, remote locations, team members, or your home office.

**Built-in Architecture:** Tailscale runs directly inside the main container (no sidecar needed). It starts automatically when `TS_AUTHKEY` is set and uses userspace networking mode (no special privileges required).

## What is Tailscale?

Tailscale creates a secure, private network across all your devices. Once connected, your Claude YOLO container gets its own IP address that you can access from any device on your Tailscale network - no port forwarding, no firewalls, no VPN configuration.

**Perfect for:**
- 📱 Phone/tablet access from anywhere
- 🏠 Access from home when traveling
- 👥 Team sharing (multiple people accessing the same environment)
- 🔒 Secure remote access without exposing ports

## Quick Start

### 1. Get a Tailscale Auth Key

1. Sign up for Tailscale (free): https://login.tailscale.com/start
2. Go to Settings → Keys: https://login.tailscale.com/admin/settings/keys
3. Generate a new auth key:
   - **Reusable:** Yes (recommended for containers)
   - **Ephemeral:** No (unless you want it to disappear when container stops)
   - **Tags:** Optional, use `tag:container` for organization
   - **Expiration:** Set based on your needs (90 days is common)

4. Copy the key (starts with `tskey-auth-...`)

### 2. Configure Your Environment

Edit `.env` and add your Tailscale auth key:

```bash
# Required
TS_AUTHKEY=tskey-auth-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional - customize hostname (default: claude-yolo)
TS_HOSTNAME=claude-yolo-dev
```

### 3. Start the Container

```bash
# Tailscale starts automatically when TS_AUTHKEY is set
docker-compose up -d

# Or use convenience targets
make up-tailscale          # Verifies TS_AUTHKEY is set
make up-tailscale-web      # Tailscale + web terminal
```

### 4. Find Your Container's IP

```bash
# Check Tailscale status
make tailscale-status

# You'll see output like:
# 100.64.x.x   claude-yolo-dev    user@    linux   -
```

### 5. Access from Any Device

**From your phone/tablet:**
1. Install Tailscale app
2. Log in with same account
3. Browse to: `http://claude-yolo-dev:7681` (if web terminal enabled)
4. Or SSH: Use your favorite mobile SSH client

**From another computer:**
```bash
# SSH (if you have SSH keys configured)
ssh developer@claude-yolo-dev

# Web browser (if web terminal enabled)
http://claude-yolo-dev:7681

# Direct access to container services
curl http://claude-yolo-dev:8000
```

## Configuration Options

### Environment Variables

All configuration is done via `.env`:

```bash
# === Required ===
TS_AUTHKEY=tskey-auth-xxxxxxxxxxxxx
  # Get from: https://login.tailscale.com/admin/settings/keys

# === Optional ===
TS_HOSTNAME=claude-yolo-dev
  # Default: claude-yolo
  # This becomes your hostname on the Tailscale network

TS_ACCEPT_DNS=false
  # Default: false
  # Set to true if you want to use Tailscale's MagicDNS

TS_EXTRA_ARGS=
  # Examples:
  # --advertise-routes=10.0.0.0/8  (advertise subnet routes)
  # --accept-routes                 (accept routes from other nodes)
  # --ssh                           (enable Tailscale SSH)
```

### Advanced: Subnet Routes

If you want to access other services on your network through this container:

```bash
# In .env
TS_EXTRA_ARGS=--advertise-routes=192.168.1.0/24

# Then approve the routes in Tailscale admin console
```

### Advanced: Tailscale SSH

Enable Tailscale's built-in SSH (no key management needed):

```bash
# In .env
TS_EXTRA_ARGS=--ssh

# Then SSH from any Tailscale device without SSH keys
```

## Use Cases

### 1. Phone Access

Perfect for checking on long-running tasks while away from your desk:

1. Install Tailscale app on phone
2. Connect to your Tailnet
3. Open browser: `http://claude-yolo:7681`
4. Full terminal access from your phone!

### 2. Team Sharing

Share your environment with team members for demos or collaboration:

1. Generate auth key with appropriate tags
2. Share the Tailscale hostname with team
3. Team members can access via their Tailscale connection
4. Optional: Use ACLs to control who can access what

**ACL Example** (in Tailscale admin console):
```json
{
  "acls": [
    {
      "action": "accept",
      "src": ["group:engineering"],
      "dst": ["tag:container:*"]
    }
  ]
}
```

### 3. Remote Access from Home

Working from office but need to check something from home:

1. Start container with Tailscale at office
2. Access from home via Tailscale
3. No port forwarding or VPN configuration needed
4. Secure, encrypted connection

### 4. Multi-Location Access

Access the same environment from multiple locations:

1. Container running on server/cloud
2. Access from laptop, phone, tablet, home computer
3. All devices see the same Tailscale IP
4. Perfect for consistent development environment

## Combining with Web Terminal

The best experience is to use Tailscale + Web Terminal together:

```bash
# Start both
make up-tailscale-web

# Access from anywhere
http://claude-yolo:7681
```

Benefits:
- No SSH client needed
- Works on any device with browser
- Phone/tablet friendly
- File upload/download support
- Persistent sessions (tmux)

## Security Considerations

### Authentication Layers

With Tailscale + Web Terminal, you have **two layers of security**:

1. **Tailscale Network:** Only devices on your Tailnet can access
2. **Web Terminal Auth:** Optional password protection

**Recommended Setup:**

**For personal use:**
```bash
# Just Tailscale is enough (no web terminal auth needed)
TS_AUTHKEY=your-key
# No WEBTERMINAL_AUTH needed
```

**For team sharing:**
```bash
# Add web terminal auth as second layer
TS_AUTHKEY=your-key
WEBTERMINAL_AUTH=admin:team-password
```

### Auth Key Security

**Best Practices:**
- ✅ Use **reusable** keys for containers (they can restart)
- ✅ Use **ephemeral** keys for testing (auto-cleanup)
- ✅ Add **tags** like `tag:container` for organization
- ✅ Set appropriate **expiration** (90 days typical)
- ❌ Don't share keys publicly
- ❌ Don't commit `.env` to git (already in `.gitignore`)

### ACLs (Access Control Lists)

Control who can access your container via Tailscale admin console:

```json
{
  "tagOwners": {
    "tag:container": ["user@example.com"]
  },
  "acls": [
    {
      "action": "accept",
      "src": ["user@example.com"],
      "dst": ["tag:container:*"]
    }
  ]
}
```

## Troubleshooting

### Can't connect to Tailscale

1. **Check container is running:**
   ```bash
   docker ps | grep claude-yolo
   ```

2. **Check Tailscale logs:**
   ```bash
   make tailscale-logs
   # Or
   tail -f logs/tailscale.log
   ```

3. **Verify auth key:**
   ```bash
   # Check .env file
   grep TS_AUTHKEY .env

   # Make sure it starts with tskey-auth-
   ```

4. **Check Tailscale status:**
   ```bash
   make tailscale-status
   # Or
   docker exec claude-yolo sudo tailscale status
   ```

### Container appears in Tailscale but can't access

1. **Verify container is healthy:**
   ```bash
   docker ps
   # Look for "healthy" status
   ```

2. **Check firewall on host machine:**
   ```bash
   # Tailscale uses UDP port 41641
   # Usually auto-configured, but worth checking
   ```

3. **Try accessing via IP instead of hostname:**
   ```bash
   # Get IP from: make tailscale-status
   curl http://100.64.x.x:7681
   ```

### Auth key expired or invalid

Error: `"authkey expired"` or similar

**Solution:**
1. Generate new auth key
2. Update `.env` with new key
3. Restart: `make restart`

### DNS not resolving hostname

If `claude-yolo` doesn't resolve:

**Option 1:** Use IP address directly
```bash
# Get IP from: make tailscale-status
http://100.64.x.x:7681
```

**Option 2:** Enable MagicDNS (in Tailscale admin)
1. Go to DNS settings
2. Enable MagicDNS
3. Restart container

### Multiple containers showing same hostname

If you run multiple claude-yolo instances:

```bash
# Set unique hostnames in each .env
TS_HOSTNAME=claude-yolo-dev-1
TS_HOSTNAME=claude-yolo-dev-2
```

## Comparison with Alternatives

### Tailscale vs Port Forwarding

**Tailscale:**
- ✅ Secure by default (encrypted)
- ✅ No router configuration
- ✅ Works through NAT/firewalls
- ✅ Access control via ACLs
- ✅ Works from anywhere
- ❌ Requires Tailscale on all devices

**Port Forwarding:**
- ✅ No additional software
- ❌ Security risk (exposed to internet)
- ❌ Router configuration required
- ❌ Breaks when IP changes
- ❌ Difficult access control

### Tailscale vs Traditional VPN

**Tailscale:**
- ✅ Zero configuration
- ✅ Peer-to-peer (fast)
- ✅ Per-device access control
- ✅ Cross-platform
- ✅ Free for personal use

**Traditional VPN:**
- ❌ Complex setup
- ❌ Centralized (slower)
- ❌ All-or-nothing access
- ❌ Expensive

### Tailscale vs SSH Tunneling

**Tailscale:**
- ✅ Persistent connection
- ✅ Multiple protocols
- ✅ Mobile-friendly
- ✅ Team sharing easy

**SSH Tunneling:**
- ✅ No additional service
- ❌ Manual setup each time
- ❌ Breaks on disconnect
- ❌ Difficult on mobile

## Advanced Scenarios

### Running Multiple Instances

Each instance needs unique hostname:

```bash
# Instance 1: .env
TS_HOSTNAME=claude-yolo-dev
WEBTERMINAL_PORT=7681

# Instance 2: .env
TS_HOSTNAME=claude-yolo-prod
WEBTERMINAL_PORT=7682
```

### Sharing with External Team

1. Create Tailscale auth key with tag
2. Add ACL for external users
3. Share hostname and credentials
4. External users join your Tailnet
5. They can access the container

### Exit Node (Route All Traffic)

Use container as exit node:

```bash
# In .env
TS_EXTRA_ARGS=--advertise-exit-node

# Then approve in Tailscale admin
# Other devices can route all traffic through this container
```

## Disabling Tailscale

```bash
# Option 1: Remove TS_AUTHKEY from .env and restart
# Comment out or remove TS_AUTHKEY from .env
make restart

# Option 2: Stop the container entirely
make down

# Option 3: Manually stop Tailscale inside running container
docker exec claude-yolo sudo tailscale down
```

## Additional Resources

- [Tailscale Documentation](https://tailscale.com/kb/)
- [Tailscale Docker Guide](https://tailscale.com/kb/1282/docker)
- [Tailscale ACLs](https://tailscale.com/kb/1018/acls)
- [Tailscale SSH](https://tailscale.com/kb/1193/tailscale-ssh)
- [MagicDNS](https://tailscale.com/kb/1081/magicdns)

## FAQ

**Q: Does Tailscale cost money?**
A: Free for personal use (up to 100 devices, 3 users). Paid plans for teams.

**Q: Is this secure?**
A: Yes. Tailscale uses WireGuard for encryption. Connections are peer-to-peer when possible.

**Q: Can I use this in production?**
A: Yes, but consider:
- Use reusable auth keys with appropriate expiration
- Set up ACLs for access control
- Enable monitoring/logging
- Consider Tailscale team plan for better support

**Q: What if my auth key expires?**
A: Container will lose Tailscale connection. Generate new key and restart.

**Q: Can I access localhost services from remote?**
A: Yes! Services running in the container are accessible via the Tailscale IP.

**Q: Does this work with MCP servers?**
A: Yes. MCP servers running in the container are accessible via Tailscale network.
