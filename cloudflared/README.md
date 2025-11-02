# Cloudflare Tunnel Integration

Expose your Claude YOLO environment to the public internet securely through Cloudflare's global network - no port forwarding, no firewall configuration, no VPN client needed. Perfect for demos, customer access, and remote collaboration.

**Built-in Architecture:** Cloudflared runs directly inside the main container (no sidecar needed). It starts automatically when `CLOUDFLARED_TUNNEL_TOKEN` or `CLOUDFLARED_CONFIG` is set. Unlike Tailscale and OpenVPN, cloudflared doesn't require special Linux capabilities.

## What is Cloudflare Tunnel?

Cloudflare Tunnel creates a secure, outbound-only connection from your container to Cloudflare's edge network. Your services become accessible via a public URL (or custom domain) without exposing your local network or opening ports.

**Perfect for:**
- 🎯 **Sales Demos** - Instant public URLs for customer demos
- 🤝 **Client Access** - Share terminal/services with clients (no VPN setup)
- 👥 **Team Collaboration** - Remote team access without Tailscale/VPN client
- 🌍 **Public Web Terminal** - Browser-based access from anywhere
- 🔒 **Zero Trust** - Built-in Cloudflare Access for authentication

## Quick Start (Token Method - Easiest)

### 1. Create a Cloudflare Tunnel

1. Sign up for Cloudflare (free): https://dash.cloudflare.com/sign-up
2. Go to Zero Trust → Access → Tunnels: https://one.dash.cloudflare.com/
3. Click "Create a tunnel"
4. Choose "Cloudflared"
5. Name your tunnel (e.g., `claude-yolo-demo`)
6. Copy the tunnel token (long string starting with `ey...`)

### 2. Configure Your Environment

Edit `.env` and add your tunnel token:

```bash
# Simplest method - just paste the token
CLOUDFLARED_TUNNEL_TOKEN=eyJhIjoiY2xhdWRlLXlvbG8tZGVtbyIsInMi...
```

### 3. Configure Public Hostname

Back in Cloudflare dashboard:
1. Under "Public Hostname" tab, click "Add a public hostname"
2. **Subdomain:** `claude-demo` (or your choice)
3. **Domain:** Select your domain (or use `*.cfargotunnel.com` for testing)
4. **Service:**
   - Type: `HTTP`
   - URL: `localhost:7681` (for web terminal) or `localhost:8000` (for your app)
5. Click "Save"

### 4. Start the Container

```bash
# Cloudflared starts automatically when token is set
docker-compose up -d

# Check tunnel status
make cloudflared-status
```

### 5. Access Your Container

Your services are now publicly accessible:
```
https://claude-demo.yourdomain.com
# or
https://claude-demo.cfargotunnel.com
```

No VPN client needed - just open in any browser!

## Configuration Methods

### Method 1: Token-Based (Recommended for Quick Start)

Simplest method - configure everything in Cloudflare dashboard:

```bash
# In .env
CLOUDFLARED_TUNNEL_TOKEN=eyJhIjoiY2xhdWRlLXlvbG8tZGVtbyIsInMi...
```

**Pros:**
- Easiest to set up
- Configure routes in web UI
- No local config files needed

**Cons:**
- Less portable (tied to dashboard)
- Harder to version control configuration

### Method 2: Config File (Advanced/Reproducible)

For complex routing or version control:

1. Create `cloudflared/config.yml`:
```yaml
tunnel: <your-tunnel-id>
credentials-file: /home/developer/.cloudflared/<tunnel-id>.json

ingress:
  # Web terminal
  - hostname: terminal.yourdomain.com
    service: http://localhost:7681

  # Application
  - hostname: app.yourdomain.com
    service: http://localhost:8000

  # SSH access
  - hostname: ssh.yourdomain.com
    service: ssh://localhost:22

  # Catch-all (required)
  - service: http_status:404
```

2. Place credentials file:
```bash
# Download from Cloudflare and place in cloudflared/
# Will be mounted to /home/developer/.cloudflared/ in container
```

3. Configure `.env`:
```bash
CLOUDFLARED_CONFIG=config.yml
```

## Use Cases

### 1. Sales Engineering - Instant Demos

Share a live demo with customers instantly:

```bash
# In .env
CLOUDFLARED_TUNNEL_TOKEN=your-token
WEBTERMINAL_ENABLED=true
WEBTERMINAL_AUTH=demo:secure-password

# Start
docker-compose up -d

# Share with customer
echo "Demo: https://demo.yourdomain.com (user: demo, pass: secure-password)"
```

**Benefits:**
- No "can you open port 8000?" conversations
- Works through corporate firewalls
- Professional custom domain
- Optional Cloudflare Access for SSO

### 2. Customer Support - Shared Terminal

Let customers access a shared terminal for troubleshooting:

```bash
# Configure tunnel to expose web terminal
# Set strong WEBTERMINAL_AUTH password
# Share link with customer

# Customer opens browser (no SSH client needed!)
https://support.yourdomain.com
```

### 3. Remote Team Access (No VPN)

Unlike Tailscale, team members don't need to install anything:

```bash
# Set up tunnel with Cloudflare Access
# Configure allowed email domains
# Share link with team

# Team members:
# 1. Click link
# 2. Authenticate via SSO (Google, GitHub, etc.)
# 3. Access terminal/app in browser
```

### 4. Public Web Terminal

Make your container accessible from any device:

```bash
CLOUDFLARED_TUNNEL_TOKEN=your-token
WEBTERMINAL_ENABLED=true
# Add Cloudflare Access for security!

# Access from:
# - Phone browser
# - Tablet
# - Public computer
# - Any device anywhere
```

### 5. API/Webhook Development

Expose local API for webhook testing:

```bash
# Tunnel configuration
# Service: http://localhost:8000

# Now external services can reach your local API:
curl https://api.yourdomain.com/webhook
```

## Security Configuration

### Option 1: Web Terminal Password (Basic)

```bash
# In .env
WEBTERMINAL_AUTH=admin:strong-password-here
```

Single-factor protection. Fine for demos, not for sensitive data.

### Option 2: Cloudflare Access (Recommended)

Add zero-trust authentication:

1. Go to Cloudflare Zero Trust → Access → Applications
2. Click "Add an application"
3. **Application type:** Self-hosted
4. **Application name:** Claude YOLO Terminal
5. **Session Duration:** 12 hours
6. **Application domain:** `terminal.yourdomain.com`
7. **Policy:**
   - **Policy name:** Email authentication
   - **Action:** Allow
   - **Include:** Emails ending in `@yourcompany.com`
8. Save

Now only authorized emails can access!

### Option 3: Cloudflare Access + GitHub/Google SSO

Enterprise-grade security:

1. Configure Cloudflare Access (above)
2. Add identity provider:
   - Go to Settings → Authentication
   - Add GitHub or Google as provider
3. Update policy to require GitHub/Google login
4. Optional: Add country restrictions, IP allowlists

**Result:** Users must authenticate with GitHub/Google before accessing.

## Advanced Configuration

### Multiple Services

Route different domains to different services:

In Cloudflare dashboard or `config.yml`:
```yaml
ingress:
  - hostname: terminal.yourdomain.com
    service: http://localhost:7681

  - hostname: api.yourdomain.com
    service: http://localhost:8000

  - hostname: metrics.yourdomain.com
    service: http://localhost:9090

  - service: http_status:404
```

### Metrics and Monitoring

Enable cloudflared metrics:

```bash
# In .env
CLOUDFLARED_METRICS_PORT=9099

# Access metrics inside container
docker exec claude-yolo curl localhost:9099/metrics
```

Metrics include:
- Tunnel connectivity
- Request counts
- Error rates
- Latency

### SSH Over Tunnel

Access container via SSH through Cloudflare:

1. Configure ingress for SSH:
```yaml
- hostname: ssh.yourdomain.com
  service: ssh://localhost:22
```

2. Install cloudflared on client machine
3. Configure SSH config:
```
Host ssh.yourdomain.com
  ProxyCommand cloudflared access ssh --hostname %h
```

4. SSH directly:
```bash
ssh developer@ssh.yourdomain.com
```

### Custom Domains

Use your own domain instead of `cfargotunnel.com`:

1. Add domain to Cloudflare
2. Update DNS (automatic if nameservers pointed to Cloudflare)
3. Use domain in tunnel configuration
4. Cloudflare handles SSL certificates automatically

## Combining with Other Services

### Cloudflared + Web Terminal

Perfect combination for remote access:

```bash
CLOUDFLARED_TUNNEL_TOKEN=your-token
WEBTERMINAL_ENABLED=true
WEBTERMINAL_AUTH=user:pass

# Result: Public web terminal accessible from anywhere
```

### Cloudflared + Tailscale

Best of both worlds:

```bash
CLOUDFLARED_TUNNEL_TOKEN=your-token  # Public access
TS_AUTHKEY=your-key                   # Private Tailnet access

# Use cases:
# - Cloudflared: Customer/demo access (public)
# - Tailscale: Personal access (private, no SSO friction)
```

### Cloudflared + OpenVPN

Access corporate resources while exposing public interface:

```bash
OPENVPN_CONFIG=corporate.ovpn        # Connect to internal network
CLOUDFLARED_TUNNEL_TOKEN=your-token  # Expose publicly

# Container connected to VPN, accessible publicly
# Perfect for demos requiring internal API access
```

## Troubleshooting

### Tunnel Not Connecting

```bash
# Check logs
make cloudflared-logs
# or
tail -f logs/cloudflared.log

# Common errors:
# - "authentication error" → Token invalid/expired
# - "tunnel not found" → Tunnel deleted in dashboard
# - "no route to host" → Network connectivity issue
```

**Solutions:**
1. Verify token is correct (check .env)
2. Check tunnel still exists in Cloudflare dashboard
3. Ensure container has internet access

### Can Access Tunnel But Service Not Working

**Symptoms:** URL loads but shows error

**Diagnosis:**
```bash
# Check if service is running in container
docker exec claude-yolo curl localhost:7681
docker exec claude-yolo curl localhost:8000

# Check cloudflared logs for routing errors
make cloudflared-logs
```

**Solutions:**
1. Verify service port matches tunnel configuration
2. Check service is actually running
3. Review ingress rules in dashboard or config

### Slow Response Times

**Symptoms:** Pages load slowly

**Possible causes:**
- Geographic distance to Cloudflare edge
- Upstream service (in container) is slow
- Network congestion

**Solutions:**
```bash
# Check metrics
docker exec claude-yolo curl localhost:9099/metrics | grep latency

# Test service locally (should be fast)
docker exec claude-yolo curl -w '%{time_total}\n' localhost:7681

# If local is fast but public is slow → Cloudflare routing
# If local is also slow → service performance issue
```

### "Bad Gateway" Errors

**Symptoms:** 502 Bad Gateway from Cloudflare

**Common causes:**
1. Service not running on configured port
2. Wrong protocol (HTTPS when should be HTTP)
3. Service crashed/restarting

**Diagnosis:**
```bash
# Verify service is accessible locally
docker exec claude-yolo curl -I localhost:7681

# Check cloudflared status
docker exec claude-yolo ps aux | grep cloudflared
```

## Comparison with Alternatives

### Cloudflared vs Tailscale

**Cloudflared:**
- ✅ No client software needed (just browser)
- ✅ Public internet access
- ✅ Perfect for demos/customers
- ✅ Built-in DDoS protection
- ✅ Free SSL certificates
- ❌ Public exposure (need access control)
- ❌ Requires domain/setup

**Tailscale:**
- ✅ Private network only
- ✅ Zero configuration access control
- ✅ Peer-to-peer (can be faster)
- ❌ Requires Tailscale client
- ❌ Not suitable for public demos

**Best practice:** Use both! Cloudflared for demos/public, Tailscale for private access.

### Cloudflared vs ngrok

**Cloudflared:**
- ✅ Free (no limits on Cloudflare Free plan)
- ✅ Custom domains
- ✅ No random URLs
- ✅ Enterprise SSO/access control
- ✅ DDoS protection
- ❌ Requires Cloudflare account
- ❌ More setup steps

**ngrok:**
- ✅ Simpler initial setup
- ✅ No account needed (free tier)
- ❌ Random URLs (free tier)
- ❌ Limited requests (free tier)
- ❌ No built-in SSO
- ❌ Custom domains require paid plan

### Cloudflared vs Port Forwarding

**Cloudflared:**
- ✅ No router configuration
- ✅ Works through NAT/firewalls
- ✅ Built-in SSL
- ✅ DDoS protection
- ✅ Access control
- ✅ Doesn't expose your IP

**Port Forwarding:**
- ✅ No third-party service
- ❌ Exposes your home/office IP
- ❌ Requires router access
- ❌ No SSL (have to set up)
- ❌ No DDoS protection
- ❌ Security nightmare

## Makefile Commands

```bash
# Check tunnel status and connectivity
make cloudflared-status

# View real-time cloudflared logs
make cloudflared-logs

# Start with cloudflared enabled
make up-cloudflared

# Start with cloudflared + web terminal
make up-cloudflared-web
```

## Disabling Cloudflared

```bash
# Option 1: Remove token from .env and restart
# Comment out or remove CLOUDFLARED_TUNNEL_TOKEN
make restart

# Option 2: Stop container
make down

# Option 3: Manually stop inside running container
docker exec claude-yolo pkill cloudflared
```

## Best Practices

### For Demos

```bash
# Use token method (easiest)
CLOUDFLARED_TUNNEL_TOKEN=your-token

# Enable web terminal with password
WEBTERMINAL_ENABLED=true
WEBTERMINAL_AUTH=demo:YourSecurePassword123

# Use memorable subdomain
# Configure in Cloudflare: demo.yourcompany.com
```

### For Production

```bash
# Use config file (version control)
CLOUDFLARED_CONFIG=config.yml

# Enable Cloudflare Access with SSO
# Configure country restrictions
# Enable audit logs
# Set up monitoring/alerts

# Consider rate limiting
# Use Web Application Firewall (WAF)
```

### Security Checklist

- ✅ Use Cloudflare Access for sensitive data
- ✅ Enable audit logging
- ✅ Set session timeouts
- ✅ Use strong WEBTERMINAL_AUTH passwords
- ✅ Monitor access logs
- ✅ Rotate tunnel tokens periodically
- ❌ Don't commit tokens to git (already in .gitignore)
- ❌ Don't use weak passwords for public-facing terminals
- ❌ Don't expose sensitive services without access control

## Additional Resources

- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Cloudflare Access](https://developers.cloudflare.com/cloudflare-one/applications/configure-apps/)
- [Cloudflared GitHub](https://github.com/cloudflare/cloudflared)
- [Zero Trust Dashboard](https://one.dash.cloudflare.com/)

## FAQ

**Q: Is Cloudflare Tunnel free?**
A: Yes! Free tier includes up to 50 users on Cloudflare Access. Perfect for small teams and demos.

**Q: Can I use this without a custom domain?**
A: Yes, use `*.cfargotunnel.com` subdomains for testing. For production, custom domains are recommended.

**Q: How secure is this?**
A: Very secure when configured properly:
- All traffic encrypted (TLS)
- No inbound ports opened on your network
- Optional zero-trust authentication
- DDoS protection from Cloudflare

**Q: Can I expose SSH access?**
A: Yes! Configure ingress with `ssh://localhost:22` and use cloudflared SSH client.

**Q: What about rate limiting?**
A: Configure in Cloudflare WAF/Rate Limiting rules. Protects against abuse.

**Q: Can customers access without Cloudflare account?**
A: Yes! They just open the URL. You control access via Cloudflare Access (email whitelist, SSO, etc.).

**Q: How is this different from a reverse proxy?**
A: Cloudflare Tunnel is a reverse proxy, but:
- Outbound-only (no inbound firewall rules)
- Managed by Cloudflare (no nginx/apache config)
- Built-in SSL, DDoS protection, global CDN

**Q: Can I run multiple tunnels?**
A: Yes! Create multiple tunnels in Cloudflare dashboard, each with different token. One container can only run one tunnel at a time though.

**Q: What if I delete the tunnel in Cloudflare dashboard?**
A: Cloudflared will fail to connect. Create a new tunnel and update token in `.env`.

**Q: Performance vs direct access?**
A: Adds 10-50ms latency (routing through Cloudflare edge). Usually imperceptible for web terminals and APIs. Cloudflare's global network often makes it faster than home upload speeds!
