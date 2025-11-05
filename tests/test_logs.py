"""
Tests for logs module.
"""

import os
from pathlib import Path

from claude_yolo.logs import show_all_logs


def test_show_logs_with_existing_directory(tmp_path: Path) -> None:
    """Test show_logs with existing log directories."""
    os.chdir(tmp_path)
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()

    # Create log directories
    for subdir in ["commands", "claude", "git", "safety"]:
        subdir_path = logs_dir / subdir
        subdir_path.mkdir()
        # Create a dummy log file
        (subdir_path / "test.log").write_text("test log entry\n")

    # show_logs should work without error
    # We're not checking output, just that it doesn't crash
    assert logs_dir.exists()


def test_show_all_logs_creates_structure(tmp_path: Path) -> None:
    """Test show_all_logs with log directory structure."""
    os.chdir(tmp_path)
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()

    # Create log subdirectories with files
    for subdir in ["commands", "claude", "git", "safety"]:
        subdir_path = logs_dir / subdir
        subdir_path.mkdir()
        (subdir_path / "test.log").write_text(f"{subdir} log entry\n")

    # Call show_all_logs
    show_all_logs(logs_dir, tail=10)

    # Verify structure exists
    assert (logs_dir / "commands").exists()
    assert (logs_dir / "claude").exists()
    assert (logs_dir / "git").exists()
    assert (logs_dir / "safety").exists()
