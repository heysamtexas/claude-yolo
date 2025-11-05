# Web Terminal Access

Access your Claude YOLO environment from any web browser - perfect for remote access, mobile devices, or when you can't (or don't want to) use SSH.

## Quick Start

```bash
# Start with web terminal enabled
docker-compose -f docker-compose.yml -f docker-compose.webterminal.yml up -d

# Or use the Makefile shortcut
make up-web

# Access at: http://localhost:7681
```

## Features

- **Browser-Based**: Access from any device with a web browser
- **Full Terminal**: Complete bash shell with all container features
- **File Transfer**: Built-in zmodem support for file uploads/downloads
- **Reconnection**: Survives network hiccups and browser restarts
- **Customizable**: Dark theme, configurable font size
- **Optional Auth**: Password protection for security
- **Stable**: Runs inside container (no docker exec instability)

## Configuration

### Port Configuration

Edit `.env` to change the port:

```bash
WEBTERMINAL_PORT=7681  # Default port
```

### Authentication (Recommended for Remote Access)

Add password protection by setting in `.env`:

```bash
WEBTERMINAL_AUTH=username:password
```

Example:
```bash
WEBTERMINAL_AUTH=admin:your_secure_password_here
```

Then restart:
```bash
docker-compose -f docker-compose.yml -f docker-compose.webterminal.yml restart
```

## Security Considerations

The web terminal runs directly inside the Claude YOLO container, making it more secure and stable than sidecar approaches.

### Recommended Security Setup

**For Local Development (Low Risk):**
```bash
# No auth needed if only accessing from localhost
WEBTERMINAL_PORT=7681
# Access: http://localhost:7681
```

**For Remote Access (Medium Risk):**
```bash
# Require authentication
WEBTERMINAL_AUTH=admin:strong_password_here
WEBTERMINAL_PORT=7681

# Access via SSH tunnel:
ssh -L 7681:localhost:7681 your-server
# Then open: http://localhost:7681
```

**For Team/Corporate (Higher Security):**
Use a reverse proxy with SSL:

```nginx
# nginx config example
server {
    listen 443 ssl;
    server_name claude-terminal.yourcompany.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:7681;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Advanced Configuration

The web terminal is configured via environment variables. To customize beyond defaults, you can:

1. **Adjust font size**: Edit `config/init.sh` and change `fontSize=16`
2. **Change theme**: Edit the theme JSON in `config/init.sh`
3. **Disable write access**: Remove `--writable` flag in `config/init.sh`

## File Transfer

The web terminal supports file transfer via zmodem protocol:

**Upload files:**
1. In the terminal, run: `rz`
2. Select files in the browser dialog
3. Files upload to current directory

**Download files:**
1. In the terminal, run: `sz filename`
2. File downloads via browser

Note: `lrzsz` package should be installed (already included in the container).

## Troubleshooting

### Can't connect to web terminal

1. **Check container is running:**
   ```bash
   docker ps | grep claude-yolo
   ```

2. **Check logs:**
   ```bash
   # Container logs (includes ttyd startup)
   docker logs claude-yolo

   # Web terminal specific logs
   docker exec claude-yolo cat /logs/webterminal.log
   ```

3. **Verify port is exposed:**
   ```bash
   docker port claude-yolo
   ```

### Terminal keeps disconnecting

The new architecture (ttyd running inside the container) is much more stable. If you still experience disconnections:

1. **Check container health:**
   ```bash
   docker stats claude-yolo
   ```

2. **Look for crashes in logs:**
   ```bash
   tail -f logs/webterminal.log
   ```

3. **Try increasing resources** in `.env`:
   ```bash
   CONTAINER_MEMORY_LIMIT=6G
   ```

### Authentication not working

- Format must be `username:password` (colon-separated)
- No spaces around the colon
- Restart container after changing `.env`

### Port already in use

Change the port in `.env`:
```bash
WEBTERMINAL_PORT=7682  # Or any other available port
```

## Mobile Access

The web terminal works great on mobile devices:

- **iPhone/iPad**: Open Safari, navigate to http://your-ip:7681
- **Android**: Use Chrome or Firefox
- **Tablet**: Keyboard shortcuts work with external keyboard

**Tips for mobile:**
- Font size is already optimized (16px)
- Use landscape mode for more screen space
- Enable authentication for security

## Comparison with Alternatives

### Web Terminal vs SSH

**Web Terminal Pros:**
- No SSH client needed
- Works through corporate firewalls (HTTP/HTTPS)
- Access from any device
- Easy file transfer
- More stable (no docker exec)

**SSH Pros:**
- More secure by default
- Better performance for large data transfers
- More mature/tested

### Web Terminal vs VS Code Server

**Web Terminal:**
- Lightweight (minimal overhead)
- Instant startup
- Terminal-focused
- Simple setup

**VS Code Server:**
- Full IDE experience
- File browsing, editing
- Extensions support
- Higher resource usage

## Use Cases

**Perfect for:**
- Remote server access
- Mobile/tablet work
- Corporate environments with SSH restrictions
- Quick access without local setup
- Team demonstrations
- Emergency access from any device
- Working from public computers

**Not ideal for:**
- Heavy development work (use VS Code)
- High-security requirements (use SSH with keys)
- Low-bandwidth connections

## Stopping Web Terminal

```bash
# Stop entire setup
docker-compose -f docker-compose.yml -f docker-compose.webterminal.yml down

# Or restart to disable web terminal
docker-compose -f docker-compose.yml up -d

# Or use Makefile
make down
make up  # Without -web flag
```

## Logs

Web terminal logs are saved to `/logs/webterminal.log` inside the container and accessible from the host in the `logs/` directory:

```bash
# View from host
tail -f logs/webterminal.log

# Or from inside container
docker exec claude-yolo tail -f /logs/webterminal.log
```

## Additional Resources

- [ttyd documentation](https://github.com/tsl0922/ttyd)
- [WebSocket basics](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [Reverse proxy setup guides](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
