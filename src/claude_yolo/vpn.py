"""
VPN management for claude-yolo.
"""

from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


def handle_vpn_command(subcommand: str) -> None:
    """
    Handle VPN subcommands.

    Args:
        subcommand: VPN subcommand (status, connect, disconnect)
    """
    if subcommand == "status":
        show_vpn_status()
    else:
        console.print(f"[yellow]VPN command '{subcommand}' not yet implemented[/yellow]")
        console.print("\nAvailable commands:")
        console.print("  • [cyan]status[/cyan]  - Show VPN connection status")


def show_vpn_status() -> None:
    """Show status of all VPN/proxy services."""
    console.print("[bold]VPN/Proxy Status[/bold]\n")

    env_file = Path.cwd() / ".env"

    if not env_file.exists():
        console.print("[yellow]No .env file found[/yellow]")
        return

    # Parse .env file
    vpn_features = {
        "ENABLE_TAILSCALE": "Tailscale VPN",
        "ENABLE_OPENVPN": "OpenVPN",
        "ENABLE_CLOUDFLARED": "Cloudflared Tunnel",
    }

    table = Table(show_header=True)
    table.add_column("Service", style="cyan")
    table.add_column("Enabled", justify="center")
    table.add_column("Status")

    try:
        with env_file.open() as f:
            env_content = f.read()

            for var, name in vpn_features.items():
                enabled = f"{var}=true" in env_content
                status_text = "[green]Enabled[/green]" if enabled else "[dim]Disabled[/dim]"
                connection_status = "N/A" if not enabled else check_vpn_connection(var)

                table.add_row(name, status_text, connection_status)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error reading .env: {e}[/red]")


def check_vpn_connection(vpn_type: str) -> str:
    """
    Check if a VPN service is actually connected.

    Args:
        vpn_type: VPN environment variable name

    Returns:
        Connection status string
    """
    # TODO: Implement actual connection checks
    # This would require checking inside the container
    return "[dim]Unknown[/dim]"
