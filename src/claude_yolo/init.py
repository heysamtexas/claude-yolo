"""
Project initialization logic for claude-yolo.
"""

import shutil
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .utils import generate_unique_name

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


def setup_git_config(home_dir: Path) -> None:
    """
    Auto-detect host git configuration and pre-populate home/.gitconfig.

    This allows the container to automatically use the developer's git identity
    without manual configuration.

    Args:
        home_dir: Path to the home directory (project_dir/home)
    """
    gitconfig_path = home_dir / ".gitconfig"

    # Skip if .gitconfig already exists (don't overwrite user customizations)
    if gitconfig_path.exists():
        console.print("  ℹ️  Git config already exists, skipping auto-detection")
        return

    try:
        # Try to get git user.name and user.email from host
        git_name = subprocess.run(
            ["git", "config", "--global", "user.name"],
            capture_output=True,
            text=True,
            timeout=2
        ).stdout.strip()

        git_email = subprocess.run(
            ["git", "config", "--global", "user.email"],
            capture_output=True,
            text=True,
            timeout=2
        ).stdout.strip()

        if git_name and git_email:
            # Create a minimal .gitconfig with the user's identity
            gitconfig_content = f"""[user]
\tname = {git_name}
\temail = {git_email}
[init]
\tdefaultBranch = main
[pull]
\trebase = false
"""
            gitconfig_path.write_text(gitconfig_content)
            console.print(f"  ✓ Auto-detected git config: {git_name} <{git_email}>")
        else:
            console.print("  ℹ️  No host git config found - container will use defaults")

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        # Git not installed or not configured - not an error, just skip
        console.print("  ℹ️  Could not detect host git config - container will use defaults")
        pass


def init_project(project_dir: Path, minimal: bool = False) -> None:
    """
    Initialize claude-yolo in the given project directory.

    Args:
        project_dir: Directory to initialize (usually current directory)
        minimal: If True, skip VPN/proxy configurations
    """
    claude_dir = project_dir / ".claude-yolo"

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
        # Skip VPN configs if minimal mode (but still create empty dirs for Docker mounts)
        if minimal and item.name in MINIMAL_EXCLUDE:
            if item.is_dir():
                # Create empty directory for Docker mount compatibility
                dest = claude_dir / item.name
                dest.mkdir(parents=True, exist_ok=True)
                console.print(f"  ○ Created empty {item.name}/ (minimal mode)")
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

    # Create logs directory with subdirectories inside .claude-yolo/
    console.print("\n📊 Creating .claude-yolo/logs/ directory...")
    log_subdirs = [
        "commands",
        "claude",
        "git",
        "safety",
    ]
    logs_dir = claude_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.chmod(0o755)
    for subdir in log_subdirs:
        subdir_path = logs_dir / subdir
        subdir_path.mkdir(parents=True, exist_ok=True)
        subdir_path.chmod(0o755)
    console.print(f"  ✓ Created {len(log_subdirs)} log subdirectories with proper permissions")

    # Create home directory inside .claude-yolo/ (for container user configs)
    console.print("\n🏠 Creating .claude-yolo/home/ directory...")
    home_dir = claude_dir / "home"
    home_dir.mkdir(parents=True, exist_ok=True)
    home_dir.chmod(0o755)
    console.print("  ✓ Created home/ with proper permissions")

    # Auto-detect and copy host git config
    setup_git_config(home_dir)

    # Create .env inside .claude-yolo/
    env_file = claude_dir / ".env"
    if not env_file.exists():
        console.print("\n⚙️  Creating .claude-yolo/.env file...")

        # Generate unique container name based on project directory
        unique_name = generate_unique_name(project_dir)
        console.print(f"  ℹ️  Generated unique name: {unique_name}")

        env_template = claude_dir / ".env.example"
        if env_template.exists():
            # Copy template and inject unique name
            env_content = env_template.read_text()
            env_content = env_content.replace("CONTAINER_NAME=claude-yolo", f"CONTAINER_NAME={unique_name}")
            # Add COMPOSE_PROJECT_NAME if not present (check for actual assignment, not just text)
            if "COMPOSE_PROJECT_NAME=" not in env_content:
                env_content = env_content.replace(
                    f"CONTAINER_NAME={unique_name}",
                    f"CONTAINER_NAME={unique_name}\nCOMPOSE_PROJECT_NAME={unique_name}"
                )
            env_file.write_text(env_content)
            console.print("  ✓ Created .env from template with unique name")
        else:
            # Fallback: create minimal .env with unique name
            env_file.write_text(generate_default_env(unique_name))
            console.print("  ✓ Created default .env with unique name")
    else:
        console.print("\n⚙️  .env already exists, skipping...")

    # Create .claude-yolo/.gitignore to prevent committing infrastructure state
    console.print("\n📝 Creating .claude-yolo/.gitignore...")
    gitignore_file = claude_dir / ".gitignore"
    gitignore_file.write_text("*\n")
    console.print("  ✓ Created .gitignore (ignores all .claude-yolo/ contents)")

    # Success message with next steps
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        Markdown(get_success_message(minimal)),
        title="[bold green]✨ claude-yolo initialized successfully![/bold green]",
        border_style="green"
    ))


def generate_default_env(container_name: str = "claude-yolo") -> str:
    """
    Generate a minimal default .env file.

    Args:
        container_name: Unique container name (auto-generated or default)
    """
    return f"""# Claude YOLO Configuration

# Container Configuration
# Auto-generated unique name based on project directory
CONTAINER_NAME={container_name}
COMPOSE_PROJECT_NAME={container_name}
APP_PORT=8000

# Resource Limits
CPU_LIMIT=2
MEMORY_LIMIT=4g

# VPN/Proxy Configuration
ENABLE_TAILSCALE=false
ENABLE_OPENVPN=false
ENABLE_CLOUDFLARED=false

# Web Terminal
WEBTERMINAL_ENABLED=true
WEBTERMINAL_PORT=7681

# Logging
CLAUDE_LOG_LEVEL=info
"""




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

- `.claude-yolo/` - Docker configuration, scripts, logs, home directory, and .env

### Next Steps:

1. **Review configuration:**
   ```bash
   vim .claude-yolo/.env
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
