"""
Container lifecycle management for claude-yolo.
"""

import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def check_initialized(project_root: Path) -> Path:
    """
    Check if claude-yolo is initialized in the given project directory.

    Args:
        project_root: Path to the project root directory

    Returns:
        Path to .claude-yolo directory

    Raises:
        typer.Exit: If not initialized
    """
    claude_dir = project_root / ".claude-yolo"

    if not claude_dir.exists():
        console.print("[red]Error: claude-yolo not initialized in this directory.[/red]")
        console.print("\nRun [cyan]claude-yolo init[/cyan] first.")
        raise typer.Exit(1)

    return claude_dir


def run_hook(project_root: Path, hook_name: str) -> None:
    """
    Run a hook script if it exists.

    Args:
        project_root: Path to the project root directory
        hook_name: Name of the hook (e.g., "pre-build", "post-build")
    """
    claude_dir = project_root / ".claude-yolo"
    hook_file = claude_dir / "hooks" / f"{hook_name}.sh"

    if hook_file.exists() and hook_file.is_file():
        console.print(f"[dim]Running {hook_name} hook...[/dim]")
        try:
            subprocess.run(
                [str(hook_file)],
                check=True,
                cwd=claude_dir,
            )
            console.print(f"[dim]✓ {hook_name} hook completed[/dim]\n")
        except subprocess.CalledProcessError as e:
            console.print(f"[yellow]Warning: {hook_name} hook failed with code {e.returncode}[/yellow]")


def docker_compose_cmd(
    project_root: Path,
    args: list[str],
    check: bool = True,
    extra_compose_files: list[str] | None = None
) -> subprocess.CompletedProcess:
    """
    Run a docker-compose command.

    Args:
        project_root: Path to the project root directory
        args: Arguments to pass to docker-compose
        check: Whether to raise exception on non-zero exit
        extra_compose_files: Additional compose files to include (e.g., ["docker-compose.mcp.yml"])

    Returns:
        CompletedProcess instance
    """
    claude_dir = check_initialized(project_root)
    compose_file = claude_dir / "docker-compose.yml"

    if not compose_file.exists():
        console.print(f"[red]Error: docker-compose.yml not found at {compose_file}[/red]")
        raise typer.Exit(1)

    # Use --project-directory for path resolution and --env-file for .claude-yolo/.env
    env_file = claude_dir / ".env"
    cmd = [
        "docker-compose",
        "--project-directory", str(project_root),
        "--env-file", str(env_file),
        "-f", str(compose_file)
    ]

    # Add extra compose files if provided
    if extra_compose_files:
        for extra_file in extra_compose_files:
            extra_path = claude_dir / extra_file
            if not extra_path.exists():
                console.print(f"[red]Error: {extra_file} not found at {extra_path}[/red]")
                raise typer.Exit(1)
            cmd.extend(["-f", str(extra_path)])

    cmd.extend(args)

    return subprocess.run(cmd, check=check)


def build_image(project_root: Path, no_cache: bool = False, pull: bool = True) -> None:
    """
    Build the Docker image.

    Args:
        project_root: Path to the project root directory
        no_cache: Build without using cache
        pull: Pull latest base images
    """
    check_initialized(project_root)

    # Run pre-build hook
    run_hook(project_root, "pre-build")

    console.print("[bold]Building Docker image...[/bold]")

    args = ["build"]
    if no_cache:
        args.append("--no-cache")
    if pull:
        args.append("--pull")

    try:
        docker_compose_cmd(project_root, args)
        console.print("\n[green]✓ Build completed successfully[/green]")

        # Run post-build hook
        run_hook(project_root, "post-build")

    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]✗ Build failed with exit code {e.returncode}[/red]")
        raise typer.Exit(e.returncode) from None


def run_container(project_root: Path, detach: bool = False, build_first: bool = True, mcp: bool = False) -> None:
    """
    Start the container.

    Args:
        project_root: Path to the project root directory
        detach: Run in background
        build_first: Build image before starting
        mcp: Enable MCP OAuth mode (host networking)
    """
    check_initialized(project_root)

    if build_first:
        console.print("[dim]Building image first...[/dim]\n")
        build_image(project_root, no_cache=False, pull=False)
        console.print()

    # Run pre-start hook
    run_hook(project_root, "pre-start")

    # Show MCP mode message if enabled
    if mcp:
        console.print("[bold cyan]🔐 Running in MCP OAuth mode (host networking)[/bold cyan]")
        console.print("[dim]Note: Cannot join other Docker networks in this mode[/dim]\n")

    console.print("[bold]Starting container...[/bold]")

    args = ["up"]
    if detach:
        args.append("-d")

    # Add MCP compose file if MCP mode is enabled
    extra_files = ["docker-compose.mcp.yml"] if mcp else None

    try:
        docker_compose_cmd(project_root, args, extra_compose_files=extra_files)

        if detach:
            console.print("\n[green]✓ Container started in background[/green]")
            if mcp:
                console.print("[cyan]  MCP OAuth callbacks will work on any port[/cyan]")
            console.print("\nView logs: [cyan]claude-yolo logs --follow[/cyan]")
            console.print("Open shell: [cyan]claude-yolo shell[/cyan]")
        else:
            console.print("\n[dim]Container stopped[/dim]")

    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]✗ Failed to start container (exit code {e.returncode})[/red]")
        raise typer.Exit(e.returncode) from None
    except KeyboardInterrupt:
        console.print("\n[yellow]Container stopped by user[/yellow]")


def exec_shell(project_root: Path) -> None:
    """
    Open a shell in the running container.

    Args:
        project_root: Path to the project root directory
    """
    check_initialized(project_root)

    console.print("[cyan]Opening shell in container...[/cyan]\n")

    # Get container name from .env or use default
    container_name = get_container_name(project_root)

    cmd = ["docker", "exec", "-it", container_name, "/bin/bash"]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            console.print("\n[red]Container is not running.[/red]")
            console.print("Start it with: [cyan]claude-yolo run[/cyan]")
        else:
            console.print(f"\n[red]Failed to open shell (exit code {e.returncode})[/red]")
        raise typer.Exit(e.returncode) from None


def stop_container(project_root: Path) -> None:
    """
    Stop the container.

    Args:
        project_root: Path to the project root directory
    """
    check_initialized(project_root)

    console.print("[bold]Stopping container...[/bold]")

    try:
        docker_compose_cmd(project_root, ["stop"])
        console.print("\n[green]✓ Container stopped[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]✗ Failed to stop container (exit code {e.returncode})[/red]")
        raise typer.Exit(e.returncode) from None


def restart_container(project_root: Path, build_first: bool = False) -> None:
    """
    Restart the container.

    Args:
        project_root: Path to the project root directory
        build_first: Rebuild image before restarting
    """
    check_initialized(project_root)

    if build_first:
        console.print("[dim]Rebuilding image...[/dim]\n")
        build_image(project_root, no_cache=False, pull=False)
        console.print()

    console.print("[bold]Restarting container...[/bold]")

    try:
        docker_compose_cmd(project_root, ["restart"])
        console.print("\n[green]✓ Container restarted[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]✗ Failed to restart container (exit code {e.returncode})[/red]")
        raise typer.Exit(e.returncode) from None


def clean_resources(project_root: Path, volumes: bool = False, force: bool = False) -> None:
    """
    Clean up containers and optionally volumes.

    Args:
        project_root: Path to the project root directory
        volumes: Also remove volumes
        force: Don't ask for confirmation
    """
    check_initialized(project_root)

    if not force:
        message = "Remove containers"
        if volumes:
            message += " and volumes (this will delete all data)"
        message += "?"

        if not typer.confirm(message):
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit(0)

    console.print("[bold]Cleaning up resources...[/bold]")

    args = ["down"]
    if volumes:
        args.append("-v")

    try:
        docker_compose_cmd(project_root, args)
        console.print("\n[green]✓ Cleanup complete[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]✗ Cleanup failed (exit code {e.returncode})[/red]")
        raise typer.Exit(e.returncode) from None


def show_status(project_root: Path) -> None:
    """
    Show status of the container and resources.

    Args:
        project_root: Path to the project root directory
    """
    check_initialized(project_root)

    console.print("[bold]Claude YOLO Status[/bold]\n")

    # Get container status
    container_name = get_container_name(project_root)

    try:
        result = subprocess.run(
            ["docker", "inspect", container_name],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            # Container exists
            import json
            data = json.loads(result.stdout)[0]

            state = data["State"]
            config = data["Config"]

            # Create status table
            table = Table(title="Container Information", show_header=False)
            table.add_column("Property", style="cyan")
            table.add_column("Value")

            table.add_row("Name", container_name)
            table.add_row("Status", get_status_badge(state["Status"]))
            table.add_row("Image", config["Image"])

            if state["Running"]:
                table.add_row("Uptime", state.get("StartedAt", "Unknown"))

            # Show resource usage if running
            if state["Running"]:
                try:
                    stats_result = subprocess.run(
                        ["docker", "stats", container_name, "--no-stream", "--format",
                         "{{.CPUPerc}}\t{{.MemUsage}}"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    cpu, mem = stats_result.stdout.strip().split("\t")
                    table.add_row("CPU Usage", cpu)
                    table.add_row("Memory Usage", mem)
                except (subprocess.CalledProcessError, ValueError):
                    pass

            console.print(table)
            console.print()

            # Show enabled features
            show_enabled_features()

        else:
            console.print(f"[yellow]Container '{container_name}' does not exist[/yellow]")
            console.print("\nRun [cyan]claude-yolo run[/cyan] to start the container.")

    except Exception as e:
        console.print(f"[red]Error checking status: {e}[/red]")


def get_status_badge(status: str) -> str:
    """
    Get a colored badge for the status.

    Args:
        status: Container status string

    Returns:
        Formatted status string
    """
    status_colors = {
        "running": "green",
        "exited": "red",
        "paused": "yellow",
        "restarting": "yellow",
        "dead": "red",
    }

    color = status_colors.get(status.lower(), "white")
    return f"[{color}]{status}[/{color}]"


def show_enabled_features() -> None:
    """Show which features are enabled."""
    env_file = Path.cwd() / ".env"

    if not env_file.exists():
        return

    features = {
        "ENABLE_TAILSCALE": "Tailscale VPN",
        "ENABLE_OPENVPN": "OpenVPN",
        "ENABLE_CLOUDFLARED": "Cloudflared Tunnel",
        "ENABLE_WEB_TERMINAL": "Web Terminal",
    }

    enabled = []

    try:
        with env_file.open() as f:
            env_content = f.read()

            for var, name in features.items():
                if f"{var}=true" in env_content:
                    enabled.append(name)

        if enabled:
            console.print("[bold]Enabled Features:[/bold]")
            for feature in enabled:
                console.print(f"  • {feature}")
            console.print()

    except Exception:
        pass


def get_container_name(project_root: Path) -> str:
    """
    Get the container name from .claude-yolo/.env or use default.

    Args:
        project_root: Path to the project root directory

    Returns:
        Container name
    """
    env_file = project_root / ".claude-yolo" / ".env"

    if env_file.exists():
        try:
            with env_file.open() as f:
                for line in f:
                    if line.startswith("CONTAINER_NAME="):
                        return line.split("=", 1)[1].strip()
        except Exception:
            pass

    return "claude-yolo"
