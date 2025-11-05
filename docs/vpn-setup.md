# VPN & Remote Access Setup

Configure secure remote access to your claude-yolo environment using Tailscale, OpenVPN, or Cloudflare Tunnel.

## Overview

claude-yolo supports three remote access methods:

| Method | Best For | Setup Time | Network Type |
|--------|----------|------------|--------------|
| **Tailscale** | Personal use, team sharing, mobile access | 5 minutes | Private mesh network |
| **OpenVPN** | Corporate VPN, accessing internal resources | 10-15 minutes | Point-to-site VPN |
| **Cloudflare Tunnel** | Public demos, customer access, webhooks | 10 minutes | Public internet (secure) |

**You can enable multiple methods simultaneously!**

---

## Tailscale Setup

**Perfect for:** Accessing your environment from anywhere (phone, laptop, tablet), team collaboration, secure mesh networking.

### Quick Start

1. **Get an auth key** from https://login.tailscale.com/admin/settings/keys
   - Click "Generate auth key"
   - Optional: Enable "Reusable" and set expiration
   - Recommended: Tag with `tag:container`

2. **Configure in `.env`:**
```bash
TS_AUTHKEY=tskey-auth-xxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxx
TS_HOSTNAME=claude-yolo-dev
```

3. **Start the container:**
```bash
claude-yolo run
```

4. **Access from anywhere:**
   - Find your container IP: https://login.tailscale.com/admin/machines
   - Access your app: `http://<hostname>:8000`
   - Web terminal: `http://<hostname>:7681`
   - From phone: Install Tailscale app, same URLs work!

### Configuration Options

#### Basic Settings
```bash
# Required: Your auth key
TS_AUTHKEY=tskey-auth-xxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Custom hostname (default: claude-yolo)
TS_HOSTNAME=my-dev-environment

# Optional: Accept DNS from Tailscale (default: false)
TS_ACCEPT_DNS=false
```

#### Advanced Settings
```bash
# Advertise routes (make your local network accessible)
TS_EXTRA_ARGS=--advertise-routes=10.0.0.0/8

# Accept routes from other nodes
TS_EXTRA_ARGS=--accept-routes

# Enable Tailscale SSH
TS_EXTRA_ARGS=--ssh

# Combine multiple options
TS_EXTRA_ARGS=--advertise-routes=10.0.0.0/8 --accept-routes --ssh
```

### Use Cases

**Mobile Development Testing:**
```bash
# Access from your phone to test mobile views
TS_HOSTNAME=mobile-dev-${USER}
```

**Team Collaboration:**
```bash
# Share environment with team
TS_HOSTNAME=team-shared-env

# Team members can access same URL
# No port forwarding or public IP needed!
```

**Multi-Device Development:**
```bash
# Work on desktop, review on laptop, test on tablet
# Same environment, accessible from all devices
```

### Troubleshooting Tailscale

**"Auth key expired":**
```bash
# Generate new key with longer expiration
# Or use reusable key: https://login.tailscale.com/admin/settings/keys
```

**"Cannot resolve hostname":**
```bash
# Use IP address instead
# Find IP at: https://login.tailscale.com/admin/machines

# Or enable MagicDNS in Tailscale admin
```

**"Connection refused":**
```bash
# Check container is running
claude-yolo status

# Check firewall rules
# Tailscale should automatically handle firewall traversal
```

---

## OpenVPN Setup

**Perfect for:** Connecting to corporate VPN, accessing internal APIs/databases, private network resources.

### Quick Start

1. **Get OpenVPN config** from your network admin
   - Usually a `.ovpn` file
   - May include embedded certificates

2. **Place config file:**
```bash
# Copy your .ovpn file to the openvpn directory
cp ~/Downloads/company-vpn.ovpn .claude-yolo/openvpn/
```

3. **Configure in `.env`:**
```bash
# Enable OpenVPN
OPENVPN_CONFIG=company-vpn.ovpn

# If your VPN uses username/password (not certificate-based)
OPENVPN_AUTH_USER=your-username
OPENVPN_AUTH_PASS=your-password
```

4. **Start the container:**
```bash
claude-yolo run
```

5. **Verify connection:**
```bash
# Open shell
claude-yolo shell

# Check VPN is connected
ip addr show tun0

# Test internal access
curl http://internal-api.company.local/health
```

### Configuration File Setup

**Minimal .ovpn file:**
```
client
dev tun
proto udp
remote vpn.company.com 1194
resolv-retry infinite
nobind
persist-key
persist-tun
ca ca.crt
cert client.crt
key client.key
cipher AES-256-CBC
verb 3
```

**With inline certificates:**
```
client
dev tun
proto udp
remote vpn.company.com 1194

<ca>
-----BEGIN CERTIFICATE-----
[certificate content]
-----END CERTIFICATE-----
</ca>

<cert>
-----BEGIN CERTIFICATE-----
[certificate content]
-----END CERTIFICATE-----
</cert>

<key>
-----BEGIN PRIVATE KEY-----
[key content]
-----END PRIVATE KEY-----
</key>
```

### Authentication Methods

**Certificate-based (most secure):**
```bash
# No username/password needed
# Certificates are in the .ovpn file or separate files
OPENVPN_CONFIG=company-vpn.ovpn
```

**Username/Password:**
```bash
OPENVPN_CONFIG=company-vpn.ovpn
OPENVPN_AUTH_USER=jdoe
OPENVPN_AUTH_PASS=SecurePassword123
```

**Two-Factor Authentication:**
```bash
# For 2FA/MFA, you may need to use auth-user-pass with a script
# Contact your network admin for instructions
```

### Multiple VPN Configs

Switch between different VPN configs:

```bash
# Development VPN
OPENVPN_CONFIG=dev-vpn.ovpn

# Production VPN
# OPENVPN_CONFIG=prod-vpn.ovpn

# Uncomment the one you need, rebuild
claude-yolo restart
```

### Troubleshooting OpenVPN

**"Auth failed":**
```bash
# Check credentials
echo $OPENVPN_AUTH_USER
echo $OPENVPN_AUTH_PASS

# Verify config file exists
ls -la .claude-yolo/openvpn/
```

**"Cannot resolve hostname":**
```bash
# Add DNS servers to .ovpn file
dhcp-option DNS 8.8.8.8
dhcp-option DNS 8.8.4.4
```

**"TLS handshake failed":**
```bash
# Check certificate validity
openssl x509 -in ca.crt -text -noout | grep "Not After"

# May need to update certificates from network admin
```

**"Connection timeout":**
```bash
# Try TCP instead of UDP
# In .ovpn file, change:
proto tcp-client  # instead of udp
```

---

## Cloudflare Tunnel Setup

**Perfect for:** Public demos, customer access, webhooks, sharing with external stakeholders, no port forwarding needed.

### Quick Start (Token Method - Easiest)

1. **Create tunnel** at https://one.dash.cloudflare.com/
   - Navigate to Access → Tunnels
   - Click "Create a tunnel"
   - Name it (e.g., "claude-yolo-demo")
   - Copy the tunnel token (starts with `ey...`)

2. **Configure public hostname** in Cloudflare dashboard:
   - Add a public hostname
   - Point to `http://localhost:8000`
   - Save

3. **Set token in `.env`:**
```bash
CLOUDFLARED_TUNNEL_TOKEN=eyJhIjoixxxxxxxxxxxxxx...
```

4. **Start the container:**
```bash
claude-yolo run
```

5. **Access publicly:**
   - Your app is now accessible at: `https://your-tunnel.example.com`
   - No firewall changes needed!
   - Works from anywhere on the internet

### Configuration Options

#### Token-Based (Recommended for Quick Start)
```bash
# Simplest method - all config in Cloudflare dashboard
CLOUDFLARED_TUNNEL_TOKEN=eyJhIjoixxxxxxxxxxxxxx...

# Optional: Enable metrics endpoint
CLOUDFLARED_METRICS_PORT=9099
```

#### Config File-Based (Advanced)

1. **Create tunnel and get credentials:**
```bash
# From your host machine (not in container)
cloudflared tunnel login
cloudflared tunnel create my-tunnel
```

2. **Create config file** `.claude-yolo/cloudflared/config.yml`:
```yaml
tunnel: <tunnel-id>
credentials-file: /etc/cloudflared/<tunnel-id>.json

ingress:
  # Main application
  - hostname: my-app.example.com
    service: http://localhost:8000

  # Web terminal
  - hostname: terminal.example.com
    service: http://localhost:7681

  # API endpoint
  - hostname: api.example.com
    path: /api/*
    service: http://localhost:8000

  # Catch-all rule (required)
  - service: http_status:404
```

3. **Copy credentials:**
```bash
# Copy the credentials file to cloudflared directory
cp ~/.cloudflared/<tunnel-id>.json .claude-yolo/cloudflared/
```

4. **Configure in `.env`:**
```bash
CLOUDFLARED_CONFIG=config.yml
```

### Security Considerations

**⚠️ Important:** Cloudflare Tunnel exposes your application to the internet!

**Enable Cloudflare Access (Zero Trust):**
```yaml
# In Cloudflare dashboard:
# Access → Applications → Add an application

# Require authentication:
# - Email OTP
# - Social login (Google, GitHub)
# - SAML/OIDC
# - mTLS
```

**IP Restrictions:**
```yaml
# In Cloudflare dashboard:
# Firewall Rules → Create rule

# Allow only specific IPs:
# (ip.src in {1.2.3.4 5.6.7.8})
```

**Rate Limiting:**
```yaml
# Enable rate limiting in Cloudflare dashboard
# Protect against DDoS and abuse
```

### Use Cases

**Customer Demos:**
```bash
# Give customers a live demo URL
# No VPN or credentials needed
# Tear down after demo with: claude-yolo clean
```

**Webhook Receivers:**
```bash
# Receive webhooks from external services
# GitHub, Stripe, Twilio, etc.
CLOUDFLARED_TUNNEL_TOKEN=ey...
# Configure webhook URL: https://my-tunnel.example.com/webhook
```

**Team Demos:**
```bash
# Share work-in-progress with team
# Accessible from any device, anywhere
# Protected by Cloudflare Access if needed
```

### Troubleshooting Cloudflare Tunnel

**"Unable to reach origin":**
```bash
# Check application is running
curl http://localhost:8000

# Check tunnel is connected
claude-yolo logs | grep cloudflared
```

**"Tunnel not found":**
```bash
# Verify token is correct
echo $CLOUDFLARED_TUNNEL_TOKEN

# Check tunnel exists in dashboard
# https://one.dash.cloudflare.com/ → Tunnels
```

**"Too many connections":**
```bash
# Free tier has connection limits
# Upgrade to paid plan or reduce connections
```

---

## Combining Multiple VPN Methods

You can enable multiple access methods simultaneously:

```bash
# .env configuration
# Tailscale for team access
TS_AUTHKEY=tskey-auth-xxxxx
TS_HOSTNAME=team-dev

# OpenVPN for corporate network
OPENVPN_CONFIG=corporate.ovpn
OPENVPN_AUTH_USER=jdoe
OPENVPN_AUTH_PASS=password

# Cloudflare for public demos
CLOUDFLARED_TUNNEL_TOKEN=ey...
```

**Use case:** Access internal corporate APIs via OpenVPN while exposing your demo to customers via Cloudflare Tunnel, and access everything from your phone via Tailscale.

---

## Checking VPN Status

```bash
# Check which VPNs are configured
claude-yolo vpn status

# Check active connections from inside container
claude-yolo shell

# Check Tailscale
tailscale status

# Check OpenVPN
ip addr show tun0

# Check Cloudflare
ps aux | grep cloudflared
```

---

## Security Best Practices

### Tailscale
- ✅ Use reusable keys with `tag:container` for better organization
- ✅ Set key expiration dates
- ✅ Enable MagicDNS for easier naming
- ✅ Use ACLs to restrict access between devices

### OpenVPN
- ✅ Use certificate-based auth when possible
- ✅ Rotate credentials regularly
- ✅ Don't commit `.ovpn` files with credentials to git
- ✅ Use company-provided VPN configs

### Cloudflare Tunnel
- ✅ Enable Cloudflare Access (Zero Trust) for authentication
- ✅ Use IP restrictions when possible
- ✅ Enable rate limiting
- ✅ Monitor access logs in Cloudflare dashboard
- ⚠️ Never expose development/debug endpoints publicly
- ⚠️ Never expose admin panels without authentication

---

## Network Architecture

### Without VPN
```
You → [Firewall] → ✗ No Access ✗ → Container
```

### With Tailscale
```
You → [Tailscale Mesh Network] → Container
     ↑ Encrypted, peer-to-peer
     ↑ Works through NAT/firewalls
```

### With OpenVPN
```
You → [OpenVPN Tunnel] → [Corporate Network] → Container
     ↑ Container has access to internal resources
```

### With Cloudflare Tunnel
```
Internet → [Cloudflare Edge] → [Encrypted Tunnel] → Container
          ↑ DDoS protection
          ↑ WAF available
          ↑ Access control
```

---

## Performance Considerations

| Method | Latency | Bandwidth | Overhead |
|--------|---------|-----------|----------|
| Tailscale | Very Low (P2P) | High | Minimal |
| OpenVPN | Low-Medium | Medium-High | Low |
| Cloudflare | Low (Global CDN) | High | Low |

**Tailscale** uses direct peer-to-peer connections when possible, falling back to DERP relays.

**OpenVPN** latency depends on your VPN server location.

**Cloudflare** uses their global network with hundreds of POPs worldwide.

---

## Debugging Connection Issues

### Enable Verbose Logging

**Tailscale:**
```bash
# In container
tailscaled --verbose=2
```

**OpenVPN:**
```bash
# In .ovpn file
verb 5  # Increase verbosity (0-11)
```

**Cloudflare:**
```bash
# In config.yml
loglevel: debug
```

### Check Logs
```bash
claude-yolo logs | grep -i vpn
claude-yolo logs | grep -i tailscale
claude-yolo logs | grep -i openvpn
claude-yolo logs | grep -i cloudflared
```

---

## See Also

- [Quick Start Guide](quickstart.md)
- [Commands Reference](commands.md)
- [Customization Guide](customization.md)
- [Troubleshooting](troubleshooting.md)
