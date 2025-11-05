"""
Tests for CLI commands.
"""

from typer.testing import CliRunner

from claude_yolo.cli import app

runner = CliRunner()


def test_version():
    """Test version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "claude-yolo version" in result.stdout


def test_doctor():
    """Test doctor command."""
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Diagnostic" in result.stdout


def test_init_requires_confirmation_if_exists(tmp_path, monkeypatch):
    """Test that init asks for confirmation if .claude-yolo exists."""
    monkeypatch.chdir(tmp_path)

    # Create .claude-yolo directory
    (tmp_path / ".claude-yolo").mkdir()

    # Should ask for confirmation (which we skip)
    result = runner.invoke(app, ["init"], input="n\n")
    assert result.exit_code == 1
    assert "already exists" in result.stdout.lower()


def test_checkout_requires_repo():
    """Test that checkout requires a repository argument."""
    result = runner.invoke(app, ["checkout"])
    assert result.exit_code != 0
