"""
mitmproxy script for logging HTTP/HTTPS requests
Useful for corporate compliance and debugging Claude Code interactions
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from mitmproxy import http

# Set up logging
log_dir = Path("/home/mitmproxy/.mitmproxy/detailed_logs")
log_dir.mkdir(exist_ok=True)

# Create daily log file
log_file = log_dir / f"requests_{datetime.now().strftime('%Y%m%d')}.jsonl"


def request(flow: http.HTTPFlow) -> None:
    """
    Log outgoing requests in JSON format
    """
    request_data = {
        "timestamp": datetime.now().isoformat(),
        "type": "request",
        "method": flow.request.method,
        "url": flow.request.pretty_url,
        "host": flow.request.host,
        "path": flow.request.path,
        "headers": dict(flow.request.headers),
        "content_length": len(flow.request.content) if flow.request.content else 0,
    }

    # Optionally log request body for specific hosts (be careful with sensitive data)
    if flow.request.host in ["api.anthropic.com", "api.openai.com"]:
        try:
            if flow.request.content and len(flow.request.content) < 10000:  # Limit size
                request_data["body_preview"] = flow.request.text[:500] if flow.request.text else None
        except Exception:
            pass

    # Write to log file
    with open(log_file, "a") as f:
        f.write(json.dumps(request_data) + "\n")


def response(flow: http.HTTPFlow) -> None:
    """
    Log responses in JSON format
    """
    response_data = {
        "timestamp": datetime.now().isoformat(),
        "type": "response",
        "method": flow.request.method,
        "url": flow.request.pretty_url,
        "status_code": flow.response.status_code,
        "headers": dict(flow.response.headers),
        "content_length": len(flow.response.content) if flow.response.content else 0,
        "duration_ms": int((flow.response.timestamp_end - flow.request.timestamp_start) * 1000)
        if flow.response.timestamp_end and flow.request.timestamp_start
        else None,
    }

    # Optionally log response body preview
    if flow.request.host in ["api.anthropic.com", "api.openai.com"]:
        try:
            if flow.response.content and len(flow.response.content) < 10000:
                response_data["body_preview"] = flow.response.text[:500] if flow.response.text else None
        except Exception:
            pass

    # Write to log file
    with open(log_file, "a") as f:
        f.write(json.dumps(response_data) + "\n")


def error(flow: http.HTTPFlow) -> None:
    """
    Log errors
    """
    error_data = {
        "timestamp": datetime.now().isoformat(),
        "type": "error",
        "method": flow.request.method,
        "url": flow.request.pretty_url,
        "error": str(flow.error) if flow.error else "Unknown error",
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(error_data) + "\n")


# Log script startup
with open(log_file, "a") as f:
    f.write(
        json.dumps(
            {
                "timestamp": datetime.now().isoformat(),
                "type": "system",
                "message": "mitmproxy logging started",
            }
        )
        + "\n"
    )
