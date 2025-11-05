"""
Project initialization logic for claude-yolo.
"""

import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

# Directories to exclude when copying with --minimal flag
MINIMAL_EXCLUDE = [
    "tailscale",
    "openvpn",
    "cloudflared",
]


def get_templates_dir() -> Path:
    """Get the path to the templates directory in the installed package."""
    return Path(__file__).parent / "templates"


def init_project(project_dir: Path, minimal: bool = False) -> None:
    """
    Initialize claude-yolo in the given project directory.

    Args:
        project_dir: Directory to initialize (usually current directory)
        minimal: If True, skip VPN/proxy configurations
    """
    claude_dir = project_dir / ".claude-yolo"
    logs_dir = project_dir / "logs"
    env_file = project_dir / ".env"
    gitignore_file = project_dir / ".gitignore"

    # Check if already initialized
    if claude_dir.exists():
        console.print(
            "[yellow]Warning:[/yellow] .claude-yolo/ already exists in this directory."
        )
        if not confirm("Overwrite existing configuration?"):
            console.print("[red]Aborted.[/red]")
            raise typer.Exit(1)
        shutil.rmtree(claude_dir)

    console.print("\n[bold]Initializing claude-yolo...[/bold]\n")

    # Create .claude-yolo directory
    console.print("📁 Creating .claude-yolo/ directory...")
    claude_dir.mkdir(parents=True, exist_ok=True)

    # Copy templates
    templates_dir = get_templates_dir()
    if not templates_dir.exists():
        console.print(f"[red]Error: Templates directory not found at {templates_dir}[/red]")
        raise typer.Exit(1)

    # Copy all template files and directories
    console.print("📋 Copying template files...")
    for item in templates_dir.iterdir():
        # Skip VPN configs if minimal mode
        if minimal and item.name in MINIMAL_EXCLUDE:
            continue

        dest = claude_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
            console.print(f"  ✓ Copied {item.name}/")
        else:
            shutil.copy2(item, dest)
            console.print(f"  ✓ Copied {item.name}")

    # Make hooks executable
    hooks_dir = claude_dir / "hooks"
    if hooks_dir.exists():
        for hook in hooks_dir.glob("*.sh"):
            hook.chmod(0o755)
        console.print("  ✓ Made hooks executable")

    # Create logs directory with subdirectories (prevents Docker permission issues on macOS)
    console.print("\n📊 Creating logs/ directory...")
    log_subdirs = [
        "commands",
        "claude",
        "git",
        "safety",
    ]
    logs_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.chmod(0o755)
    for subdir in log_subdirs:
        subdir_path = logs_dir / subdir
        subdir_path.mkdir(parents=True, exist_ok=True)
        subdir_path.chmod(0o755)
    console.print(f"  ✓ Created {len(log_subdirs)} log subdirectories with proper permissions")

    # Create workspace directory (prevents Docker permission issues on macOS)
    console.print("\n📂 Creating .claude-yolo/workspace directory...")
    workspace_dir = claude_dir / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.chmod(0o755)
    console.print("  ✓ Created workspace/ with proper permissions")

    # Create .env if it doesn't exist
    if not env_file.exists():
        console.print("\n⚙️  Creating .env file...")
        env_template = claude_dir / ".env.example"
        if env_template.exists():
            shutil.copy2(env_template, env_file)
            console.print("  ✓ Created .env from template")
        else:
            # Fallback: create minimal .env
            env_file.write_text(generate_default_env())
            console.print("  ✓ Created default .env")
    else:
        console.print("\n⚙️  .env already exists, skipping...")

    # Update .gitignore
    console.print("\n📝 Updating .gitignore...")
    update_gitignore(gitignore_file)
    console.print("  ✓ Added claude-yolo entries to .gitignore")

    # Success message with next steps
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        Markdown(get_success_message(minimal)),
        title="[bold green]✨ claude-yolo initialized successfully![/bold green]",
        border_style="green"
    ))


def generate_default_env() -> str:
    """Generate a minimal default .env file."""
    return """# Claude YOLO Configuration

# Container Configuration
CONTAINER_NAME=claude-yolo
APP_PORT=8000

# Resource Limits
CPU_LIMIT=2
MEMORY_LIMIT=4g

# VPN/Proxy Configuration
ENABLE_TAILSCALE=false
ENABLE_OPENVPN=false
ENABLE_CLOUDFLARED=false

# Web Terminal
ENABLE_WEB_TERMINAL=true
WEB_TERMINAL_PORT=7681

# Logging
CLAUDE_LOG_LEVEL=info
"""


def update_gitignore(gitignore_file: Path) -> None:
    """
    Add claude-yolo-specific entries to .gitignore.

    Args:
        gitignore_file: Path to .gitignore file
    """
    entries = [
        "",
        "# claude-yolo",
        "logs/",
        ".env",
        ".claude-yolo/.env.local",
    ]

    if gitignore_file.exists():
        content = gitignore_file.read_text()
        # Check if already added
        if "# claude-yolo" in content:
            return
        # Append to existing file
        with gitignore_file.open("a") as f:
            f.write("\n".join(entries) + "\n")
    else:
        # Create new file
        gitignore_file.write_text("\n".join(entries) + "\n")


def get_success_message(minimal: bool) -> str:
    """
    Get the success message to display after initialization.

    Args:
        minimal: Whether minimal mode was used
    """
    message = """
## 🎉 Setup Complete!

Your project is now ready to use with claude-yolo.

### What was created:

- `.claude-yolo/` - Docker configuration and scripts
- `logs/` - Runtime logs directory
- `.env` - Environment configuration

### Next Steps:

1. **Review configuration:**
   ```bash
   vim .env
   ```

2. **Customize Dockerfile (optional):**
   ```bash
   vim .claude-yolo/Dockerfile
   ```

3. **Build the Docker image:**
   ```bash
   claude-yolo build
   ```

4. **Start the container:**
   ```bash
   # Regular mode (default)
   claude-yolo run

   # OR with MCP OAuth support (for Atlassian, GitHub MCP servers)
   claude-yolo run --mcp
   ```

5. **Open a shell:**
   ```bash
   claude-yolo shell
   ```

"""

    if minimal:
        message += "\n**Note:** VPN configurations were skipped (minimal mode).\n"
    else:
        message += """
### Optional: Enable VPN/Proxy

Edit `.env` and set:
- `ENABLE_TAILSCALE=true` (and add `TAILSCALE_AUTHKEY`)
- `ENABLE_OPENVPN=true` (and configure OpenVPN)
- `ENABLE_CLOUDFLARED=true` (and add tunnel token)

"""

    message += "\n📚 Documentation: https://github.com/anthropics/claude-yolo\n"

    return message


def confirm(question: str) -> bool:
    """
    Ask user for confirmation.

    Args:
        question: Question to ask

    Returns:
        True if user confirms, False otherwise
    """
    response = typer.confirm(question)
    return response
