"""
Tests for lifecycle module.
"""

import os
from pathlib import Path

import pytest

from claude_yolo.lifecycle import check_initialized, docker_compose_cmd, get_container_name


def test_check_initialized_success(tmp_path: Path) -> None:
    """Test check_initialized when .claude-yolo exists."""
    # Create .claude-yolo directory
    (tmp_path / ".claude-yolo").mkdir()

    result = check_initialized(tmp_path)
    assert result == tmp_path / ".claude-yolo"
    assert result.is_dir()


def test_check_initialized_failure(tmp_path: Path) -> None:
    """Test check_initialized when not initialized."""
    import typer

    with pytest.raises(typer.Exit) as exc_info:
        check_initialized(tmp_path)

    assert exc_info.value.exit_code == 1


def test_check_initialized_only_checks_current_dir(tmp_path: Path) -> None:
    """Test check_initialized only checks specified directory (not parent)."""
    import typer

    # Create .claude-yolo in parent
    (tmp_path / ".claude-yolo").mkdir()

    # Create subdirectory without .claude-yolo
    subdir = tmp_path / "subdir"
    subdir.mkdir()

    # Should fail because .claude-yolo is not in subdir
    with pytest.raises(typer.Exit):
        check_initialized(subdir)


def test_get_container_name_from_env(tmp_path: Path) -> None:
    """Test reading container name from .claude-yolo/.env file."""
    claude_dir = tmp_path / ".claude-yolo"
    claude_dir.mkdir()
    env_file = claude_dir / ".env"
    env_file.write_text("CONTAINER_NAME=my-test-container\n")

    name = get_container_name(tmp_path)
    assert name == "my-test-container"


def test_get_container_name_multiline_env(tmp_path: Path) -> None:
    """Test reading container name from multi-line .claude-yolo/.env file."""
    claude_dir = tmp_path / ".claude-yolo"
    claude_dir.mkdir()
    env_file = claude_dir / ".env"
    env_file.write_text(
        """
# Comment line
OTHER_VAR=value
CONTAINER_NAME=custom-name
ANOTHER_VAR=another_value
"""
    )

    name = get_container_name(tmp_path)
    assert name == "custom-name"


def test_get_container_name_default(tmp_path: Path) -> None:
    """Test default container name when .env missing or no CONTAINER_NAME."""
    # No .claude-yolo directory
    name = get_container_name(tmp_path)
    assert name == "claude-yolo"

    # .claude-yolo/.env file without CONTAINER_NAME
    claude_dir = tmp_path / ".claude-yolo"
    claude_dir.mkdir()
    env_file = claude_dir / ".env"
    env_file.write_text("OTHER_VAR=value\n")

    name = get_container_name(tmp_path)
    assert name == "claude-yolo"


def test_docker_compose_cmd_basic(tmp_path: Path) -> None:
    """Test docker_compose_cmd constructs correct command."""
    from unittest.mock import MagicMock, patch

    # Create .claude-yolo directory with docker-compose.yml
    claude_dir = tmp_path / ".claude-yolo"
    claude_dir.mkdir()
    (claude_dir / "docker-compose.yml").write_text("version: '3'")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        docker_compose_cmd(tmp_path, ["up", "-d"], check=False)

        # Verify subprocess.run was called with correct arguments
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "docker-compose"
        assert "-f" in call_args
        assert "up" in call_args
        assert "-d" in call_args


def test_docker_compose_cmd_with_file(tmp_path: Path) -> None:
    """Test docker_compose_cmd includes compose file path."""
    from unittest.mock import MagicMock, patch

    # Create .claude-yolo directory with docker-compose.yml
    claude_dir = tmp_path / ".claude-yolo"
    claude_dir.mkdir()
    (claude_dir / "docker-compose.yml").write_text("version: '3'")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        docker_compose_cmd(tmp_path, ["build"], check=False)

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "docker-compose"
        assert "-f" in call_args

        # Find the -f flag and verify next element is a path
        f_index = call_args.index("-f")
        compose_file = call_args[f_index + 1]
        assert "docker-compose.yml" in compose_file


def test_docker_compose_cmd_single_arg(tmp_path: Path) -> None:
    """Test docker_compose_cmd with single argument."""
    from unittest.mock import MagicMock, patch

    # Create .claude-yolo directory with docker-compose.yml
    claude_dir = tmp_path / ".claude-yolo"
    claude_dir.mkdir()
    (claude_dir / "docker-compose.yml").write_text("version: '3'")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        docker_compose_cmd(tmp_path, ["ps"], check=False)

        call_args = mock_run.call_args[0][0]
        assert "docker-compose" in call_args[0]
        assert "ps" in call_args


def test_docker_compose_cmd_complex(tmp_path: Path) -> None:
    """Test docker_compose_cmd with complex arguments."""
    from unittest.mock import MagicMock, patch

    # Create .claude-yolo directory with docker-compose.yml
    claude_dir = tmp_path / ".claude-yolo"
    claude_dir.mkdir()
    (claude_dir / "docker-compose.yml").write_text("version: '3'")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        docker_compose_cmd(tmp_path, ["run", "--rm", "-it", "app", "bash"], check=False)

        call_args = mock_run.call_args[0][0]
        assert "docker-compose" in call_args[0]
        assert "run" in call_args
        assert "--rm" in call_args
        assert "-it" in call_args
        assert "app" in call_args
        assert "bash" in call_args
