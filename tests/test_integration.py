"""
Integration tests for claude-yolo workflows.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from claude_yolo.init import init_project
from claude_yolo.lifecycle import check_initialized


def test_full_init_workflow(tmp_path: Path) -> None:
    """Test complete initialization workflow creates all expected components."""
    os.chdir(tmp_path)

    # Run init
    init_project(tmp_path, minimal=False)

    # Verify all components exist
    assert (tmp_path / ".claude-yolo").is_dir()

    # Verify .claude-yolo contents
    claude_dir = tmp_path / ".claude-yolo"
    assert (claude_dir / "Dockerfile").is_file()
    assert (claude_dir / "docker-compose.yml").is_file()
    assert (claude_dir / ".env.example").is_file()
    assert (claude_dir / "config").is_dir()
    assert (claude_dir / "scripts").is_dir()
    assert (claude_dir / "hooks").is_dir()

    # Verify non-minimal includes VPN configs
    assert (claude_dir / "tailscale").is_dir()
    assert (claude_dir / "openvpn").is_dir()
    assert (claude_dir / "cloudflared").is_dir()
    assert (claude_dir / "proxy").is_dir()
    assert (claude_dir / "webterminal").is_dir()

    # Verify logs structure
    # Verify logs directory inside .claude-yolo/
    logs_dir = claude_dir / "logs"
    assert (logs_dir / "commands").is_dir()
    assert (logs_dir / "claude").is_dir()
    assert (logs_dir / "git").is_dir()
    assert (logs_dir / "safety").is_dir()

    # Verify home directory inside .claude-yolo/
    assert (claude_dir / "home").is_dir()

    # Verify hooks are executable
    hooks_dir = claude_dir / "hooks"
    for hook in hooks_dir.glob("*.sh"):
        assert os.access(hook, os.X_OK), f"{hook} should be executable"

    # Verify .env was created inside .claude-yolo from template
    env_file = claude_dir / ".env"
    assert env_file.exists()
    env_content = env_file.read_text()
    # The .env should be a copy of .env.example template
    assert len(env_content) > 100  # Should have substantial content
    assert "claude" in env_content.lower() or "yolo" in env_content.lower()

    # Verify .gitignore was created inside .claude-yolo (to prevent committing state)
    gitignore_file = claude_dir / ".gitignore"
    assert gitignore_file.exists()
    gitignore_content = gitignore_file.read_text()
    assert gitignore_content.strip() == "*"


def test_minimal_init_workflow(tmp_path: Path) -> None:
    """Test minimal initialization creates empty VPN directories for Docker mount compatibility."""
    os.chdir(tmp_path)

    # Run init with minimal flag
    init_project(tmp_path, minimal=True)

    claude_dir = tmp_path / ".claude-yolo"

    # Should have empty VPN directories (for Docker mount compatibility)
    assert (claude_dir / "tailscale").exists()
    assert (claude_dir / "openvpn").exists()
    assert (claude_dir / "cloudflared").exists()

    # But they should be empty (no config files)
    assert len(list((claude_dir / "tailscale").iterdir())) == 0
    assert len(list((claude_dir / "openvpn").iterdir())) == 0
    assert len(list((claude_dir / "cloudflared").iterdir())) == 0

    # Should still have core components
    assert (claude_dir / "Dockerfile").is_file()
    assert (claude_dir / "docker-compose.yml").is_file()
    assert (claude_dir / "config").is_dir()
    assert (claude_dir / "scripts").is_dir()
    assert (claude_dir / "hooks").is_dir()


def test_init_then_check_initialized(tmp_path: Path) -> None:
    """Test that check_initialized works after init."""
    os.chdir(tmp_path)

    # Run init
    init_project(tmp_path, minimal=False)

    # check_initialized should succeed
    claude_dir = check_initialized(tmp_path)
    assert claude_dir == tmp_path / ".claude-yolo"
    assert claude_dir.is_dir()


def test_reinit_requires_confirmation(tmp_path: Path) -> None:
    """Test that re-initializing requires confirmation."""
    import typer

    os.chdir(tmp_path)

    # First init
    init_project(tmp_path, minimal=False)

    # Try to init again with confirmation = False
    with patch("claude_yolo.init.confirm", return_value=False):
        with pytest.raises(typer.Exit) as exc_info:
            init_project(tmp_path, minimal=False)
        assert exc_info.value.exit_code == 1

    # Original files should still exist
    assert (tmp_path / ".claude-yolo" / "Dockerfile").exists()


def test_reinit_with_confirmation_replaces(tmp_path: Path) -> None:
    """Test that re-initializing with confirmation replaces files."""
    os.chdir(tmp_path)

    # First init
    init_project(tmp_path, minimal=False)

    # Modify a file
    marker_file = tmp_path / ".claude-yolo" / "MARKER"
    marker_file.write_text("test")

    # Re-init with confirmation = True
    with patch("claude_yolo.init.confirm", return_value=True):
        init_project(tmp_path, minimal=False)

    # Marker file should be gone (directory was replaced)
    assert not marker_file.exists()
    # But standard files should exist
    assert (tmp_path / ".claude-yolo" / "Dockerfile").exists()


def test_init_creates_all_required_git_hooks(tmp_path: Path) -> None:
    """Test that init creates and configures git hooks properly."""
    os.chdir(tmp_path)

    init_project(tmp_path, minimal=False)

    # Check git hooks exist
    hooks_dir = tmp_path / ".claude-yolo" / "config" / "git" / "hooks"
    assert hooks_dir.is_dir()

    # Verify key hooks exist
    assert (hooks_dir / "pre-commit").exists()
    assert (hooks_dir / "pre-push").exists()

    # Verify they're executable
    assert os.access(hooks_dir / "pre-commit", os.X_OK)
    assert os.access(hooks_dir / "pre-push", os.X_OK)
