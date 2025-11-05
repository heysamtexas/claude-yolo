"""
Git repository checkout and initialization logic.
"""

import os
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from claude_yolo.init import init_project

console = Console()


def parse_repo_url(repo: str) -> tuple[str, str]:
    """
    Parse repository URL and extract clone URL and directory name.

    Supports:
    - Full URLs: https://github.com/user/repo, git@github.com:user/repo.git
    - GitHub shorthand: user/repo
    - Local paths: ../path/to/repo

    Args:
        repo: Repository identifier

    Returns:
        Tuple of (clone_url, directory_name)
    """
    # Check if it's a local path
    if Path(repo).exists() or repo.startswith(("./", "../", "/")):
        abs_path = Path(repo).resolve()
        return str(abs_path), abs_path.name

    # Check if it's GitHub shorthand (user/repo)
    if "/" in repo and not repo.startswith(("http://", "https://", "git@")):
        # Assume GitHub shorthand
        return f"https://github.com/{repo}.git", repo.split("/")[-1]

    # Full URL - extract directory name
    if repo.endswith(".git"):
        dir_name = repo.rsplit("/", 1)[-1][:-4]  # Remove .git suffix
    else:
        dir_name = repo.rsplit("/", 1)[-1]

    return repo, dir_name


def git_clone(
    repo_url: str,
    target_dir: str,
    branch: str | None = None,
    depth: int | None = None,
) -> None:
    """
    Clone a git repository.

    Args:
        repo_url: Repository URL to clone
        target_dir: Target directory name
        branch: Optional branch to checkout
        depth: Optional shallow clone depth

    Raises:
        subprocess.CalledProcessError: If git clone fails
    """
    cmd = ["git", "clone"]

    if branch:
        cmd.extend(["--branch", branch])

    if depth:
        cmd.extend(["--depth", str(depth)])

    cmd.extend([repo_url, target_dir])

    console.print(f"[cyan]Cloning {repo_url}...[/cyan]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Cloning repository...", total=None)

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            progress.update(task, completed=True)
            console.print("[green]✓ Cloned successfully[/green]")

        except subprocess.CalledProcessError as e:
            progress.update(task, completed=True)
            console.print("[red]✗ Clone failed[/red]")
            console.print(f"[red]Error: {e.stderr}[/red]")
            raise


def checkout_repo(
    repo: str,
    branch: str | None = None,
    depth: int | None = None,
    force: bool = False,
    no_interactive: bool = False,
    auto_start: bool = False,
) -> None:
    """
    Clone a repository and optionally initialize claude-yolo.

    Args:
        repo: Repository URL or GitHub shorthand
        branch: Optional branch to checkout
        depth: Optional shallow clone depth
        force: Overwrite if directory exists
        no_interactive: Skip interactive prompts
        auto_start: Automatically init, build, and start
    """
    # Parse repository URL
    repo_url, dir_name = parse_repo_url(repo)
    target_dir = Path.cwd() / dir_name

    # Check if directory exists
    if target_dir.exists():
        if force:
            console.print(f"[yellow]Warning: {dir_name} exists, removing...[/yellow]")
            import shutil
            shutil.rmtree(target_dir)
        elif no_interactive:
            console.print(f"[red]Error: {dir_name} already exists. Use --force to overwrite.[/red]")
            raise typer.Exit(1)
        else:
            if not typer.confirm(f"{dir_name} already exists. Overwrite?"):
                console.print("[red]Aborted.[/red]")
                raise typer.Exit(1)
            import shutil
            shutil.rmtree(target_dir)

    # Clone repository
    try:
        git_clone(repo_url, str(target_dir), branch=branch, depth=depth)
    except subprocess.CalledProcessError:
        console.print("\n[red]Failed to clone repository. Please check:[/red]")
        console.print("  • Repository URL is correct")
        console.print("  • You have network connectivity")
        console.print("  • You have access to the repository (for private repos)")
        console.print("  • Git is installed and configured")
        raise typer.Exit(1) from None

    # Change to cloned directory
    os.chdir(target_dir)
    console.print(f"\n[cyan]Changed directory to {dir_name}[/cyan]\n")

    # Auto-start mode
    if auto_start:
        console.print("[bold]Auto-start mode enabled[/bold]\n")
        _run_initialization_flow(auto=True)
        return

    # Non-interactive mode
    if no_interactive:
        console.print("[bold]Initializing claude-yolo...[/bold]\n")
        init_project(target_dir, minimal=False)
        return

    # Interactive mode
    console.print("[bold]Interactive setup[/bold]\n")
    _run_initialization_flow(auto=False)


def _run_initialization_flow(auto: bool) -> None:
    """
    Run the initialization flow (init, build, start).

    Args:
        auto: If True, skip prompts and run all steps
    """
    from claude_yolo.lifecycle import build_image, run_container

    # Step 1: Initialize
    should_init = auto or typer.confirm("\nInitialize claude-yolo for this project?", default=True)

    if should_init:
        try:
            init_project(Path.cwd(), minimal=False)
        except Exception as e:
            console.print(f"[red]Initialization failed: {e}[/red]")
            return

        # Step 2: Build
        should_build = auto or typer.confirm("\nBuild Docker container now?", default=True)

        if should_build:
            console.print("\n[bold]Building Docker image...[/bold]")
            console.print("[dim]This may take 5-10 minutes on first build[/dim]\n")

            try:
                build_image(no_cache=False, pull=True)
            except Exception as e:
                console.print(f"[red]Build failed: {e}[/red]")
                console.print("\nYou can build later with: [cyan]claude-yolo build[/cyan]")
                return

            # Step 3: Start
            should_start = auto or typer.confirm("\nStart container now?", default=False)

            if should_start:
                console.print("\n[bold]Starting container...[/bold]\n")
                try:
                    run_container(detach=True, build_first=False)
                except Exception as e:
                    console.print(f"[red]Start failed: {e}[/red]")
                    console.print("\nYou can start later with: [cyan]claude-yolo run[/cyan]")
                    return
            else:
                console.print("\n[dim]Skipped starting container.[/dim]")
                show_next_steps()
        else:
            console.print("\n[dim]Skipped building.[/dim]")
            show_next_steps()
    else:
        console.print("\n[dim]Skipped initialization.[/dim]")
        console.print("\nYou can initialize later with: [cyan]claude-yolo init[/cyan]")


def show_next_steps() -> None:
    """Display next steps to the user."""
    from rich.markdown import Markdown
    from rich.panel import Panel

    message = """
### Next Steps:

```bash
claude-yolo build    # Build the Docker image
claude-yolo run      # Start the container
claude-yolo shell    # Open a shell in the container
```

📚 Documentation: https://github.com/anthropics/claude-yolo
"""

    console.print()  # Print newline
    console.print(Panel.fit(
        Markdown(message),
        title="[bold]Setup Complete[/bold]",
        border_style="cyan"
    ))
