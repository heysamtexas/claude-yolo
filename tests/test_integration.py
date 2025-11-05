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
    assert (tmp_path / "logs").is_dir()
    assert (tmp_path / ".env").is_file()
    assert (tmp_path / ".gitignore").is_file()

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
    logs_dir = tmp_path / "logs"
    assert (logs_dir / "commands").is_dir()
    assert (logs_dir / "claude").is_dir()
    assert (logs_dir / "git").is_dir()
    assert (logs_dir / "safety").is_dir()

    # Verify hooks are executable
    hooks_dir = claude_dir / "hooks"
    for hook in hooks_dir.glob("*.sh"):
        assert os.access(hook, os.X_OK), f"{hook} should be executable"

    # Verify .env was created from template
    env_content = (tmp_path / ".env").read_text()
    # The .env should be a copy of .env.example template
    assert len(env_content) > 100  # Should have substantial content
    assert "claude" in env_content.lower() or "yolo" in env_content.lower()

    # Verify .gitignore was updated
    gitignore_content = (tmp_path / ".gitignore").read_text()
    assert "# claude-yolo" in gitignore_content
    assert "logs/" in gitignore_content
    assert ".env" in gitignore_content


def test_minimal_init_workflow(tmp_path: Path) -> None:
    """Test minimal initialization excludes VPN/proxy configs."""
    os.chdir(tmp_path)

    # Run init with minimal flag
    init_project(tmp_path, minimal=True)

    claude_dir = tmp_path / ".claude-yolo"

    # Should not have VPN configs
    assert not (claude_dir / "tailscale").exists()
    assert not (claude_dir / "openvpn").exists()
    assert not (claude_dir / "cloudflared").exists()

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
    claude_dir = check_initialized()
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


def test_gitignore_accumulation(tmp_path: Path) -> None:
    """Test that multiple inits don't duplicate .gitignore entries."""
    os.chdir(tmp_path)

    # Write existing .gitignore
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("# My custom rules\n*.pyc\n")

    # First init
    init_project(tmp_path, minimal=False)

    initial_content = gitignore.read_text()
    assert "# My custom rules" in initial_content
    assert "# claude-yolo" in initial_content
    initial_count = initial_content.count("# claude-yolo")

    # Second init (with confirmation)
    with patch("claude_yolo.init.confirm", return_value=True):
        init_project(tmp_path, minimal=False)

    final_content = gitignore.read_text()
    final_count = final_content.count("# claude-yolo")

    # Should not have duplicates
    assert final_count == initial_count
    # Should still have custom rules
    assert "# My custom rules" in final_content


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
