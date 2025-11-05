"""
Template update management for claude-yolo.
"""

import shutil
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console

console = Console()

# Files that should never be overwritten (user-specific)
NEVER_UPDATE = {
    ".env",
    ".env.local",
}

# Files that likely have customizations (warn before updating)
WARN_BEFORE_UPDATE = {
    "Dockerfile",  # Has USER CUSTOMIZATION sections
    "docker-compose.yml",  # Might have custom configs
}


def get_templates_dir() -> Path:
    """Get the path to the templates directory in the installed package."""
    return Path(__file__).parent / "templates"


def check_initialized() -> Path:
    """Check if project is initialized and return .claude-yolo directory."""
    claude_dir = Path.cwd() / ".claude-yolo"
    if not claude_dir.exists():
        console.print("[red]Error: Not a claude-yolo project.[/red]")
        console.print("Run [cyan]claude-yolo init[/cyan] first.")
        raise typer.Exit(1)
    return claude_dir


def categorize_files(templates_dir: Path, claude_dir: Path) -> dict:
    """
    Categorize template files as new, changed, or unchanged.

    Returns:
        dict with keys: new, changed, unchanged, never_update
    """
    result: dict[str, list[Path]] = {
        "new": [],
        "changed": [],
        "unchanged": [],
        "never_update": [],
    }

    # Recursively find all files in templates
    for template_file in templates_dir.rglob("*"):
        if template_file.is_dir():
            continue

        # Get relative path from templates root
        rel_path = template_file.relative_to(templates_dir)
        existing_file = claude_dir / rel_path

        # Check if should never update
        if rel_path.name in NEVER_UPDATE:
            result["never_update"].append(rel_path)
            continue

        # Check if file exists
        if not existing_file.exists():
            result["new"].append(rel_path)
        else:
            # Compare content
            if template_file.read_bytes() != existing_file.read_bytes():
                result["changed"].append(rel_path)
            else:
                result["unchanged"].append(rel_path)

    return result


def create_backup(claude_dir: Path) -> Path:
    """Create a timestamped backup of .claude-yolo directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = claude_dir.parent / f".claude-yolo.backup.{timestamp}"

    console.print(f"[dim]Creating backup at {backup_dir.name}/...[/dim]")
    shutil.copytree(claude_dir, backup_dir)

    return backup_dir


def update_file(template_file: Path, target_file: Path) -> None:
    """Update a single file from template."""
    # Create parent directories if needed
    target_file.parent.mkdir(parents=True, exist_ok=True)

    # Copy file, preserving permissions
    shutil.copy2(template_file, target_file)


def update_templates() -> None:
    """
    Update claude-yolo templates while preserving customizations.
    """
    console.print("[bold]📦 Checking for template updates...[/bold]\n")

    # Check initialization
    claude_dir = check_initialized()
    templates_dir = get_templates_dir()

    if not templates_dir.exists():
        console.print(f"[red]Error: Templates directory not found at {templates_dir}[/red]")
        raise typer.Exit(1)

    # Categorize files
    files = categorize_files(templates_dir, claude_dir)

    # Check if there are any updates
    if not files["new"] and not files["changed"]:
        console.print("[green]✓ All templates are up to date![/green]")
        return

    # Show what will be updated
    if files["new"]:
        console.print(f"[bold green]Found {len(files['new'])} new file(s):[/bold green]")
        for f in files["new"]:
            icon = "⚠️ " if f.name in WARN_BEFORE_UPDATE else "✨"
            console.print(f"  {icon} {f}")
        console.print()

    if files["changed"]:
        console.print(f"[bold yellow]Found {len(files['changed'])} changed file(s):[/bold yellow]")
        for f in files["changed"]:
            icon = "⚠️ " if f.name in WARN_BEFORE_UPDATE else "📝"
            console.print(f"  {icon} {f}")
        console.print()

    if files["never_update"]:
        console.print("[dim]Files that won't be updated (user configuration):[/dim]")
        for f in files["never_update"]:
            console.print(f"  • {f}")
        console.print()

    # Warn about files that might have customizations
    custom_files = [f for f in (files["new"] + files["changed"]) if f.name in WARN_BEFORE_UPDATE]
    if custom_files:
        console.print("[yellow]⚠️  Warning: The following files may have customizations:[/yellow]")
        for f in custom_files:
            console.print(f"  • {f}")
        console.print("[dim]Review your changes after updating![/dim]\n")

    # Confirm with user
    total_updates = len(files["new"]) + len(files["changed"])
    if not typer.confirm(f"Update {total_updates} file(s)?", default=True):
        console.print("[yellow]Update cancelled.[/yellow]")
        raise typer.Exit(0)

    # Create backup
    console.print()
    backup_dir = create_backup(claude_dir)
    console.print(f"[green]✓ Backup created at {backup_dir.name}/[/green]\n")

    # Update files
    console.print("[bold]Updating files...[/bold]")
    updated_count = 0

    for rel_path in files["new"] + files["changed"]:
        template_file = templates_dir / rel_path
        target_file = claude_dir / rel_path

        try:
            update_file(template_file, target_file)
            console.print(f"  [green]✓[/green] {rel_path}")
            updated_count += 1
        except Exception as e:
            console.print(f"  [red]✗[/red] {rel_path}: {e}")

    # Success message
    console.print("\n[bold green]🎉 Update complete![/bold green]")
    console.print(f"Updated {updated_count} file(s)")

    if custom_files:
        console.print("\n[yellow]⚠️  Remember to review customized files:[/yellow]")
        for f in custom_files:
            console.print(f"  • {f}")

    console.print(f"\nBackup available at: [cyan]{backup_dir.name}/[/cyan]")
