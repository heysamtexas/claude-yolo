"""
Tests for checkout module.
"""

from unittest.mock import MagicMock, patch

import pytest

from claude_yolo.checkout import git_clone, parse_repo_url


def test_parse_repo_url_github_shorthand() -> None:
    """Test parsing GitHub shorthand (user/repo)."""
    url, name = parse_repo_url("anthropics/claude-yolo")

    assert url == "https://github.com/anthropics/claude-yolo.git"
    assert name == "claude-yolo"


def test_parse_repo_url_github_shorthand_variations() -> None:
    """Test various GitHub shorthand formats."""
    url, name = parse_repo_url("user/repo")
    assert url == "https://github.com/user/repo.git"
    assert name == "repo"

    url, name = parse_repo_url("org-name/repo-name")
    assert url == "https://github.com/org-name/repo-name.git"
    assert name == "repo-name"


def test_parse_repo_url_full_https() -> None:
    """Test parsing full HTTPS URLs."""
    url, name = parse_repo_url("https://github.com/anthropics/claude-yolo")

    assert url == "https://github.com/anthropics/claude-yolo"
    assert name == "claude-yolo"


def test_parse_repo_url_full_https_with_git() -> None:
    """Test parsing HTTPS URLs with .git extension."""
    url, name = parse_repo_url("https://github.com/anthropics/claude-yolo.git")

    assert url == "https://github.com/anthropics/claude-yolo.git"
    assert name == "claude-yolo"


def test_parse_repo_url_ssh() -> None:
    """Test parsing SSH URLs."""
    url, name = parse_repo_url("git@github.com:anthropics/claude-yolo.git")

    assert url == "git@github.com:anthropics/claude-yolo.git"
    assert name == "claude-yolo"


def test_parse_repo_url_local_path() -> None:
    """Test parsing local file paths."""
    url, name = parse_repo_url("/path/to/local/repo")

    assert url == "/path/to/local/repo"
    assert name == "repo"

    # For relative paths, the function resolves them to absolute paths
    url, name = parse_repo_url("../relative/path/myrepo")
    # Just check the name is correct (path will be resolved to absolute)
    assert name == "myrepo"
    assert "myrepo" in url


def test_parse_repo_url_gitlab() -> None:
    """Test parsing GitLab URLs."""
    url, name = parse_repo_url("https://gitlab.com/user/project")

    assert url == "https://gitlab.com/user/project"
    assert name == "project"


@patch("subprocess.run")
def test_git_clone_basic(mock_run: MagicMock) -> None:
    """Test basic git clone command."""
    mock_run.return_value = MagicMock(returncode=0)

    git_clone("https://github.com/user/repo", "repo")

    # Verify subprocess was called
    assert mock_run.called
    args = mock_run.call_args[0][0]
    assert args[0] == "git"
    assert args[1] == "clone"
    assert "https://github.com/user/repo" in args
    assert "repo" in args


@patch("subprocess.run")
def test_git_clone_with_branch(mock_run: MagicMock) -> None:
    """Test git clone with specific branch."""
    mock_run.return_value = MagicMock(returncode=0)

    git_clone("https://github.com/user/repo", "repo", branch="develop")

    args = mock_run.call_args[0][0]
    assert "--branch" in args
    assert "develop" in args


@patch("subprocess.run")
def test_git_clone_with_depth(mock_run: MagicMock) -> None:
    """Test git clone with depth (shallow clone)."""
    mock_run.return_value = MagicMock(returncode=0)

    git_clone("https://github.com/user/repo", "repo", depth=1)

    args = mock_run.call_args[0][0]
    assert "--depth" in args
    assert "1" in args


@patch("subprocess.run")
def test_git_clone_with_branch_and_depth(mock_run: MagicMock) -> None:
    """Test git clone with both branch and depth."""
    mock_run.return_value = MagicMock(returncode=0)

    git_clone("https://github.com/user/repo", "repo", branch="main", depth=1)

    args = mock_run.call_args[0][0]
    assert "--branch" in args
    assert "main" in args
    assert "--depth" in args
    assert "1" in args


@patch("subprocess.run")
def test_git_clone_failure(mock_run: MagicMock) -> None:
    """Test git clone handles failures."""
    from subprocess import CalledProcessError

    mock_run.side_effect = CalledProcessError(1, "git", stderr="error message")

    with pytest.raises(CalledProcessError):
        git_clone("https://github.com/user/nonexistent", "nonexistent")
