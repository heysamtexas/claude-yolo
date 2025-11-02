# Proxy and Logging Setup

This optional component provides request logging and inspection capabilities, useful for:
- Corporate compliance and audit trails
- Debugging API interactions
- Understanding Claude Code's external communications
- Security monitoring

## Quick Start

Start Claude YOLO with proxy enabled:

```bash
docker-compose -f docker-compose.yml -f docker-compose.proxy.yml up -d
```

## Components

### mitmproxy
- HTTP/HTTPS proxy with inspection capabilities
- Web interface at http://localhost:8081
- All requests flow through proxy on port 8080

### Request Logging
- Detailed logs in `/logs/proxy/detailed_logs/`
- JSON Lines format (one JSON object per line)
- Daily rotation (one file per day)
- Includes request/response metadata, timing, and previews

## Log Format

Each log entry is a JSON object with:

```json
{
  "timestamp": "2025-11-01T13:45:23.123456",
  "type": "request|response|error|system",
  "method": "POST",
  "url": "https://api.anthropic.com/v1/messages",
  "status_code": 200,
  "content_length": 1234,
  "duration_ms": 456,
  "body_preview": "..."
}
```

## Analyzing Logs

View logs in real-time:
```bash
tail -f logs/proxy/detailed_logs/requests_$(date +%Y%m%d).jsonl | jq '.'
```

Filter by host:
```bash
cat logs/proxy/detailed_logs/*.jsonl | jq 'select(.host == "api.anthropic.com")'
```

Calculate average response times:
```bash
cat logs/proxy/detailed_logs/*.jsonl | jq -s '[.[] | select(.type == "response")] | [.[].duration_ms] | add / length'
```

## Security Considerations

- Proxy logs may contain sensitive information
- API keys and tokens in headers are logged
- Request/response body previews are limited to 500 characters
- Only certain hosts have body logging enabled (see `log_requests.py`)
- Logs directory should have restricted permissions

## Custom Scripts

Add custom mitmproxy scripts to `proxy/scripts/`:
- Scripts automatically loaded by mitmproxy
- See [mitmproxy docs](https://docs.mitmproxy.org/stable/addons-examples/) for examples

## Disabling Proxy

To run without proxy, use standard docker-compose:

```bash
docker-compose up -d
```

## Certificate Trust

For HTTPS inspection, install mitmproxy's CA certificate:

1. Access web interface: http://localhost:8081
2. Download certificate for your OS
3. Install in system trust store
4. Restart container

Note: This is optional - proxy works without cert trust but won't decrypt HTTPS.
