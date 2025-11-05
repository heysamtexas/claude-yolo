"""
Main CLI entry point for claude-yolo.
"""

from pathlib import Path

import typer
from rich.console import Console

from claude_yolo import __version__

app = typer.Typer(
    name="claude-yolo",
    help="Claude Code YOLO mode - Docker environment with safety features",
    add_completion=False,
)
console = Console()


@app.command()
def init(
    minimal: bool = typer.Option(
        False, "--minimal", help="Skip VPN/proxy configs for minimal setup"
    )
) -> None:
    """
    Initialize claude-yolo in the current project.

    Creates .claude-yolo/ directory with Dockerfile, docker-compose.yml,
    configs, scripts, and logs/ directory for runtime logs.
    """
    from claude_yolo.init import init_project

    init_project(Path.cwd(), minimal=minimal)


@app.command()
def checkout(
    repo: str = typer.Argument(..., help="Git repository URL or GitHub shorthand (user/repo)"),
    branch: str | None = typer.Option(None, "--branch", "-b", help="Branch to checkout"),
    depth: int | None = typer.Option(None, "--depth", help="Shallow clone depth (e.g., 1)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite if directory exists"),
    no_interactive: bool = typer.Option(
        False, "--no-interactive", help="Skip interactive prompts, use defaults"
    ),
    auto_start: bool = typer.Option(
        False, "--auto-start", help="Automatically init, build, and start after checkout"
    ),
) -> None:
    """
    Clone a git repository and optionally initialize claude-yolo.

    Examples:

        claude-yolo checkout https://github.com/user/repo

        claude-yolo checkout user/repo --branch=develop

        claude-yolo checkout user/repo --depth=1 --auto-start
    """
    from claude_yolo.checkout import checkout_repo

    checkout_repo(
        repo=repo,
        branch=branch,
        depth=depth,
        force=force,
        no_interactive=no_interactive,
        auto_start=auto_start,
    )


@app.command()
def build(
    no_cache: bool = typer.Option(False, "--no-cache", help="Build without using cache"),
    pull: bool = typer.Option(True, "--pull/--no-pull", help="Pull latest base images"),
) -> None:
    """
    Build the Docker image for this project.

    Detects changes in Dockerfile and rebuilds intelligently.
    Runs pre-build hooks if configured.
    """
    from claude_yolo.lifecycle import build_image

    build_image(no_cache=no_cache, pull=pull)


@app.command()
def run(
    detach: bool = typer.Option(False, "--detach", "-d", help="Run container in background"),
    build_first: bool = typer.Option(True, "--build/--no-build", help="Build before running"),
    mcp: bool = typer.Option(False, "--mcp", help="Enable MCP OAuth mode (host networking)"),
) -> None:
    """
    Start the claude-yolo container.

    Mounts current directory as /workspace and starts all configured services.

    Use --mcp flag for MCP server authentication (Atlassian, GitHub, etc.)
    which enables host networking for OAuth callbacks.
    """
    from claude_yolo.lifecycle import run_container

    run_container(detach=detach, build_first=build_first, mcp=mcp)


@app.command()
def shell() -> None:
    """
    Open a shell in the running claude-yolo container.

    Executes /bin/bash in the container as the developer user.
    """
    from claude_yolo.lifecycle import exec_shell

    exec_shell()


@app.command()
def stop() -> None:
    """
    Stop the claude-yolo container.
    """
    from claude_yolo.lifecycle import stop_container

    stop_container()


@app.command()
def restart(
    build_first: bool = typer.Option(False, "--build", help="Rebuild before restarting"),
) -> None:
    """
    Restart the claude-yolo container.
    """
    from claude_yolo.lifecycle import restart_container

    restart_container(build_first=build_first)


@app.command()
def clean(
    volumes: bool = typer.Option(False, "--volumes", help="Also remove volumes"),
    force: bool = typer.Option(False, "--force", "-f", help="Don't ask for confirmation"),
) -> None:
    """
    Remove claude-yolo containers and optionally volumes.
    """
    from claude_yolo.lifecycle import clean_resources

    clean_resources(volumes=volumes, force=force)


@app.command()
def logs(
    log_type: str | None = typer.Option(
        None,
        "--type",
        "-t",
        help="Log type: commands|claude|git|safety|proxy|tailscale|openvpn|cloudflared",
    ),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    tail: int = typer.Option(100, "--tail", "-n", help="Number of lines to show from end"),
) -> None:
    """
    View logs from the claude-yolo environment.

    Examples:

        claude-yolo logs                          # Show all recent logs

        claude-yolo logs --type=safety --follow   # Follow safety checks

        claude-yolo logs --type=git --tail=50     # Show last 50 git log lines
    """
    from claude_yolo.logs import show_logs

    show_logs(log_type=log_type, follow=follow, tail=tail)


@app.command()
def status() -> None:
    """
    Show status of claude-yolo container and resources.

    Displays container state, resource usage, and enabled features.
    """
    from claude_yolo.lifecycle import show_status

    show_status()


@app.command()
def doctor() -> None:
    """
    Diagnose issues with claude-yolo setup.

    Checks Docker installation, port availability, configuration, and more.
    """
    from claude_yolo.utils import run_diagnostics

    run_diagnostics()


@app.command()
def vpn(
    subcommand: str = typer.Argument(..., help="VPN subcommand: status|connect|disconnect"),
) -> None:
    """
    Manage VPN connections (Tailscale, OpenVPN, Cloudflared).

    Examples:

        claude-yolo vpn status       # Show VPN connection status
    """
    from claude_yolo.vpn import handle_vpn_command

    handle_vpn_command(subcommand)


@app.command()
def update() -> None:
    """
    Update claude-yolo templates (preserves customizations).

    Shows diff and prompts before applying changes.
    """
    from claude_yolo.update import update_templates

    update_templates()


@app.command()
def version() -> None:
    """
    Show claude-yolo version.
    """
    console.print(f"claude-yolo version {__version__}", style="bold green")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
