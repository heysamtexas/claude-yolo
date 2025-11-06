"""
Tests for init module.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from claude_yolo.init import (
    confirm,
    generate_default_env,
    get_templates_dir,
    init_project,
)


def test_get_templates_dir() -> None:
    """Test that templates directory exists and contains expected files."""
    templates_dir = get_templates_dir()

    assert templates_dir.exists()
    assert templates_dir.is_dir()
    assert (templates_dir / "Dockerfile").exists()
    assert (templates_dir / "docker-compose.yml").exists()
    assert (templates_dir / ".env.example").exists()
    assert (templates_dir / "config").exists()
    assert (templates_dir / "hooks").exists()


def test_init_project_creates_structure(tmp_path: Path) -> None:
    """Test that init_project creates all expected files and directories."""
    os.chdir(tmp_path)

    init_project(tmp_path, minimal=False)

    # Verify .claude-yolo structure
    assert (tmp_path / ".claude-yolo").is_dir()
    assert (tmp_path / ".claude-yolo" / "Dockerfile").exists()
    assert (tmp_path / ".claude-yolo" / "docker-compose.yml").exists()
    assert (tmp_path / ".claude-yolo" / "config").is_dir()
    assert (tmp_path / ".claude-yolo" / "hooks").is_dir()
    assert (tmp_path / ".claude-yolo" / "scripts").is_dir()

    # Verify logs structure inside .claude-yolo/
    assert (tmp_path / ".claude-yolo" / "logs").is_dir()
    assert (tmp_path / ".claude-yolo" / "logs" / "commands").is_dir()
    assert (tmp_path / ".claude-yolo" / "logs" / "claude").is_dir()
    assert (tmp_path / ".claude-yolo" / "logs" / "git").is_dir()
    assert (tmp_path / ".claude-yolo" / "logs" / "safety").is_dir()

    # Verify home directory inside .claude-yolo/
    assert (tmp_path / ".claude-yolo" / "home").is_dir()

    # Verify .env created inside .claude-yolo/
    assert (tmp_path / ".claude-yolo" / ".env").exists()

    # Verify .gitignore created inside .claude-yolo/ (to prevent committing state)
    assert (tmp_path / ".claude-yolo" / ".gitignore").exists()
    gitignore_content = (tmp_path / ".claude-yolo" / ".gitignore").read_text()
    assert gitignore_content.strip() == "*"


def test_init_project_minimal_excludes_vpn(tmp_path: Path) -> None:
    """Test that minimal flag creates empty VPN directories for Docker mount compatibility."""
    os.chdir(tmp_path)

    init_project(tmp_path, minimal=True)

    # Should have empty VPN directories (for Docker mount compatibility)
    assert (tmp_path / ".claude-yolo" / "tailscale").exists()
    assert (tmp_path / ".claude-yolo" / "openvpn").exists()
    assert (tmp_path / ".claude-yolo" / "cloudflared").exists()

    # But they should be empty (no config files)
    assert len(list((tmp_path / ".claude-yolo" / "tailscale").iterdir())) == 0
    assert len(list((tmp_path / ".claude-yolo" / "openvpn").iterdir())) == 0
    assert len(list((tmp_path / ".claude-yolo" / "cloudflared").iterdir())) == 0

    # Should still have core files
    assert (tmp_path / ".claude-yolo" / "Dockerfile").exists()
    assert (tmp_path / ".claude-yolo" / "config").exists()


def test_init_project_with_existing_directory(tmp_path: Path) -> None:
    """Test that init handles existing .claude-yolo directory."""
    import typer

    os.chdir(tmp_path)

    # Create first
    init_project(tmp_path, minimal=False)

    # Try to init again - should require confirmation
    # We'll patch confirm to return False (abort)
    with patch("claude_yolo.init.confirm", return_value=False):
        with pytest.raises(typer.Exit):
            init_project(tmp_path, minimal=False)


def test_generate_default_env() -> None:
    """Test that generate_default_env returns valid content."""
    env_content = generate_default_env()

    # Should contain key environment variables
    assert "CONTAINER_NAME=" in env_content
    assert "APP_PORT=" in env_content
    assert "CPU_LIMIT=" in env_content
    assert "MEMORY_LIMIT=" in env_content
    assert "ENABLE_TAILSCALE=" in env_content
    assert "ENABLE_OPENVPN=" in env_content
    assert "ENABLE_CLOUDFLARED=" in env_content
    assert "CLAUDE_LOG_LEVEL=" in env_content


def test_confirm_returns_boolean() -> None:
    """Test that confirm function works with mocked input."""
    with patch("typer.confirm", return_value=True):
        result = confirm("Test question?")
        assert result is True

    with patch("typer.confirm", return_value=False):
        result = confirm("Test question?")
        assert result is False


def test_hooks_are_executable(tmp_path: Path) -> None:
    """Test that hook scripts are made executable."""
    os.chdir(tmp_path)

    init_project(tmp_path, minimal=False)

    hooks_dir = tmp_path / ".claude-yolo" / "hooks"
    for hook_file in hooks_dir.glob("*.sh"):
        # Check if file is executable (has execute bit)
        assert os.access(hook_file, os.X_OK), f"{hook_file} should be executable"
