"""
Log viewing and management for claude-yolo.
"""

import subprocess
from pathlib import Path

import typer
from rich.console import Console

console = Console()

# Map log types to their file paths
LOG_TYPES = {
    "commands": "commands/",
    "claude": "claude/",
    "git": "git/",
    "safety": "safety/",
    "proxy": "proxy.log",
    "tailscale": "tailscale.log",
    "openvpn": "openvpn.log",
    "cloudflared": "cloudflared.log",
}


def show_logs(
    log_type: str | None = None,
    follow: bool = False,
    tail: int = 100,
) -> None:
    """
    Show logs from the claude-yolo environment.

    Args:
        log_type: Type of logs to show (or None for all)
        follow: Follow log output (like tail -f)
        tail: Number of lines to show from end
    """
    logs_dir = Path.cwd() / "logs"

    if not logs_dir.exists():
        console.print("[yellow]No logs directory found.[/yellow]")
        console.print("Logs will be created when the container runs.")
        raise typer.Exit(0)

    # If no log type specified, show all recent logs
    if log_type is None:
        show_all_logs(logs_dir, tail=tail)
        return

    # Validate log type
    if log_type not in LOG_TYPES:
        console.print(f"[red]Invalid log type: {log_type}[/red]")
        console.print(f"\nAvailable log types: {', '.join(LOG_TYPES.keys())}")
        raise typer.Exit(1)

    # Get log path
    log_path = logs_dir / LOG_TYPES[log_type]

    if not log_path.exists():
        console.print(f"[yellow]No {log_type} logs found at {log_path}[/yellow]")
        raise typer.Exit(0)

    # Show logs
    if log_path.is_dir():
        # Directory of log files - show all files
        show_directory_logs(log_path, follow=follow, tail=tail)
    else:
        # Single log file
        show_file_logs(log_path, follow=follow, tail=tail)


def show_all_logs(logs_dir: Path, tail: int = 100) -> None:
    """
    Show recent logs from all sources.

    Args:
        logs_dir: Path to logs directory
        tail: Number of lines to show
    """
    console.print("[bold]Recent logs from all sources:[/bold]\n")

    for log_type, log_path in LOG_TYPES.items():
        full_path = logs_dir / log_path

        if not full_path.exists():
            continue

        console.print(f"[cyan]═══ {log_type.upper()} ═══[/cyan]")

        if full_path.is_dir():
            # Get most recent file in directory
            files = sorted(full_path.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
            if files:
                show_file_logs(files[0], follow=False, tail=min(tail, 10))
        else:
            show_file_logs(full_path, follow=False, tail=min(tail, 10))

        console.print()


def show_directory_logs(
    dir_path: Path,
    follow: bool = False,
    tail: int = 100,
) -> None:
    """
    Show logs from all files in a directory.

    Args:
        dir_path: Path to directory containing log files
        follow: Follow log output
        tail: Number of lines to show
    """
    log_files = sorted(dir_path.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)

    if not log_files:
        console.print(f"[yellow]No log files found in {dir_path}[/yellow]")
        return

    if follow:
        # Follow the most recent file
        console.print(f"[dim]Following {log_files[0].name}...[/dim]\n")
        show_file_logs(log_files[0], follow=True, tail=tail)
    else:
        # Show most recent file
        console.print(f"[dim]Showing {log_files[0].name}[/dim]\n")
        show_file_logs(log_files[0], follow=False, tail=tail)


def show_file_logs(
    file_path: Path,
    follow: bool = False,
    tail: int = 100,
) -> None:
    """
    Show logs from a single file.

    Args:
        file_path: Path to log file
        follow: Follow log output
        tail: Number of lines to show
    """
    if not file_path.exists():
        console.print(f"[yellow]Log file not found: {file_path}[/yellow]")
        return

    if follow:
        # Use tail -f to follow the file
        try:
            subprocess.run(
                ["tail", "-f", "-n", str(tail), str(file_path)],
                check=True,
            )
        except KeyboardInterrupt:
            console.print("\n[dim]Stopped following logs[/dim]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error reading logs: {e}[/red]")
    else:
        # Read and display last N lines
        try:
            with file_path.open() as f:
                lines = f.readlines()
                for line in lines[-tail:]:
                    print(line.rstrip())
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
