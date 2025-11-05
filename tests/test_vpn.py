"""
Tests for VPN module.
"""

import os
from pathlib import Path

from claude_yolo.vpn import show_vpn_status


def test_show_vpn_status_no_env(tmp_path: Path) -> None:
    """Test VPN status when no .env file exists."""
    os.chdir(tmp_path)

    # Should not raise an error
    show_vpn_status()


def test_show_vpn_status_with_tailscale_enabled(tmp_path: Path) -> None:
    """Test VPN status shows Tailscale when enabled."""
    os.chdir(tmp_path)

    env_file = tmp_path / ".env"
    env_file.write_text(
        """
ENABLE_TAILSCALE=true
TS_AUTHKEY=tskey-test-123
"""
    )

    # Should display Tailscale status
    show_vpn_status()


def test_show_vpn_status_with_openvpn_enabled(tmp_path: Path) -> None:
    """Test VPN status shows OpenVPN when enabled."""
    os.chdir(tmp_path)

    env_file = tmp_path / ".env"
    env_file.write_text(
        """
ENABLE_OPENVPN=true
OPENVPN_CONFIG=client.ovpn
"""
    )

    show_vpn_status()


def test_show_vpn_status_with_cloudflared_enabled(tmp_path: Path) -> None:
    """Test VPN status shows Cloudflared when enabled."""
    os.chdir(tmp_path)

    env_file = tmp_path / ".env"
    env_file.write_text(
        """
ENABLE_CLOUDFLARED=true
CLOUDFLARED_TUNNEL_TOKEN=ey...
"""
    )

    show_vpn_status()


def test_show_vpn_status_all_disabled(tmp_path: Path) -> None:
    """Test VPN status when all VPNs are disabled."""
    os.chdir(tmp_path)

    env_file = tmp_path / ".env"
    env_file.write_text(
        """
ENABLE_TAILSCALE=false
ENABLE_OPENVPN=false
ENABLE_CLOUDFLARED=false
"""
    )

    show_vpn_status()


def test_show_vpn_status_multiple_enabled(tmp_path: Path) -> None:
    """Test VPN status with multiple VPNs enabled."""
    os.chdir(tmp_path)

    env_file = tmp_path / ".env"
    env_file.write_text(
        """
ENABLE_TAILSCALE=true
TS_AUTHKEY=tskey-test-123
ENABLE_OPENVPN=true
OPENVPN_CONFIG=client.ovpn
ENABLE_CLOUDFLARED=false
"""
    )

    show_vpn_status()
