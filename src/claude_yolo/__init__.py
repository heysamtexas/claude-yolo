"""
claude-yolo: Claude Code YOLO mode with safety features.

A Docker-based development environment that gives Claude Code maximum autonomy
while protecting both the host machine and users through container isolation,
git hooks, and comprehensive logging.
"""

__version__ = "0.1.0"
__author__ = "Anthropic"
__license__ = "MIT"

from claude_yolo.cli import app

__all__ = ["app", "__version__"]
