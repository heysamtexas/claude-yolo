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
    update_gitignore,
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

    # Verify logs structure
    assert (tmp_path / "logs").is_dir()
    assert (tmp_path / "logs" / "commands").is_dir()
    assert (tmp_path / "logs" / "claude").is_dir()
    assert (tmp_path / "logs" / "git").is_dir()
    assert (tmp_path / "logs" / "safety").is_dir()

    # Verify .env created
    assert (tmp_path / ".env").exists()

    # Verify .gitignore created
    assert (tmp_path / ".gitignore").exists()


def test_init_project_minimal_excludes_vpn(tmp_path: Path) -> None:
    """Test that minimal flag excludes VPN configurations."""
    os.chdir(tmp_path)

    init_project(tmp_path, minimal=True)

    # Should not have VPN configs
    assert not (tmp_path / ".claude-yolo" / "tailscale").exists()
    assert not (tmp_path / ".claude-yolo" / "openvpn").exists()
    assert not (tmp_path / ".claude-yolo" / "cloudflared").exists()

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


def test_update_gitignore_creates_new(tmp_path: Path) -> None:
    """Test that update_gitignore creates new .gitignore."""
    gitignore = tmp_path / ".gitignore"

    update_gitignore(gitignore)

    content = gitignore.read_text()
    assert "# claude-yolo" in content
    assert "logs/" in content
    assert ".env" in content


def test_update_gitignore_no_duplicates(tmp_path: Path) -> None:
    """Test that update_gitignore doesn't add duplicates."""
    gitignore = tmp_path / ".gitignore"

    # Create initial gitignore
    update_gitignore(gitignore)

    # Update again
    update_gitignore(gitignore)

    content = gitignore.read_text()
    # Should only appear once
    assert content.count("# claude-yolo") == 1


def test_update_gitignore_preserves_existing(tmp_path: Path) -> None:
    """Test that update_gitignore preserves existing content."""
    gitignore = tmp_path / ".gitignore"

    # Write existing content
    gitignore.write_text("# My project\n*.pyc\n__pycache__/\n")

    update_gitignore(gitignore)

    content = gitignore.read_text()
    assert "# My project" in content
    assert "*.pyc" in content
    assert "# claude-yolo" in content


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
