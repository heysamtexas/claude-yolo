"""
Utility functions for claude-yolo.
"""

import shutil
import subprocess
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


def run_diagnostics() -> None:
    """
    Run diagnostics to check claude-yolo setup.

    Checks:
    - Docker installation
    - Docker Compose installation
    - Docker daemon running
    - Current directory initialized
    - Configuration files present
    - Port availability
    """
    console.print("[bold]Running claude-yolo diagnostics...[/bold]\n")

    checks = []

    # Check Docker
    docker_installed = check_command_exists("docker")
    checks.append(("Docker installed", docker_installed, "Install Docker from https://docker.com"))

    if docker_installed:
        docker_running = check_docker_running()
        checks.append(("Docker daemon running", docker_running, "Start Docker Desktop or dockerd"))

    # Check Docker Compose
    compose_installed = check_command_exists("docker-compose")
    checks.append(("docker-compose installed", compose_installed, "Install docker-compose"))

    # Check Git
    git_installed = check_command_exists("git")
    checks.append(("Git installed", git_installed, "Install Git"))

    # Check initialization
    claude_dir = Path.cwd() / ".claude-yolo"
    initialized = claude_dir.exists()
    checks.append(("Project initialized", initialized, "Run 'claude-yolo init'"))

    if initialized:
        # Check required files
        dockerfile_exists = (claude_dir / "Dockerfile").exists()
        checks.append(("Dockerfile present", dockerfile_exists, "Run 'claude-yolo init' again"))

        compose_exists = (claude_dir / "docker-compose.yml").exists()
        checks.append(("docker-compose.yml present", compose_exists, "Run 'claude-yolo init' again"))

        env_exists = (Path.cwd() / ".env").exists()
        checks.append((".env file present", env_exists, "Create .env file"))

    # Check ports
    if initialized:
        ports_available = check_ports_available()
        checks.append(("Required ports available", ports_available, "Check for conflicts on ports 8000, 7681"))

    # Display results
    table = Table(title="Diagnostic Results", show_header=True)
    table.add_column("Check", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Recommendation")

    all_passed = True

    for check_name, passed, recommendation in checks:
        status = "[green]✓ PASS[/green]" if passed else "[red]✗ FAIL[/red]"
        rec_text = "[dim]OK[/dim]" if passed else recommendation

        table.add_row(check_name, status, rec_text)

        if not passed:
            all_passed = False

    console.print(table)
    console.print()

    if all_passed:
        console.print("[bold green]✨ All checks passed! Your environment is ready.[/bold green]")
    else:
        console.print("[bold yellow]⚠️  Some checks failed. Please address the recommendations above.[/bold yellow]")


def check_command_exists(command: str) -> bool:
    """
    Check if a command exists in PATH.

    Args:
        command: Command name to check

    Returns:
        True if command exists
    """
    return shutil.which(command) is not None


def check_docker_running() -> bool:
    """
    Check if Docker daemon is running.

    Returns:
        True if Docker is running
    """
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            check=False,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def check_ports_available() -> bool:
    """
    Check if required ports are available.

    Returns:
        True if ports are available
    """
    import socket

    ports_to_check = [8000, 7681]  # APP_PORT, WEB_TERMINAL_PORT

    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", port))
            sock.close()
        except OSError:
            return False

    return True
