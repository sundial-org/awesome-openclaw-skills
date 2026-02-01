import json
from typing import Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def print_result(data: Any, json_output: bool = False):
    if json_output:
        # Handle cases where data might be a dictionary or other serializable object
        print(json.dumps(data, indent=2, default=str))
        return

    if isinstance(data, dict) and "printers" in data and isinstance(data["printers"], list):
        table = Table(title="Discovered Printers")
        table.add_column("Name", style="cyan")
        table.add_column("Address", style="magenta")
        table.add_column("Alias", style="bold green")
        
        for p in data["printers"]:
            alias = p.get("alias", "--")
            table.add_row(p.get("name", "Unknown"), p.get("address", "N/A"), alias)
        console.print(table)
        
    elif isinstance(data, dict) and "message" in data:
        color = "green" if data.get("success", True) else "red"
        console.print(Panel(data["message"], style=color))
    elif isinstance(data, dict) and "default_printer" in data:
        # This is a configuration object (from whoami or config show)
        table = Table(title="inkjet Configuration")
        table.add_column("Key", style="yellow")
        table.add_column("Value", style="bold white")
        
        # Human-friendly key mapping
        key_map = {
            "default_printer": "Default Printer",
            "printers": "Saved Aliases",
            "energy": "Energy (Darkness)",
            "print_speed": "Print Speed",
            "quality": "Print Quality"
        }
        
        for k, v in data.items():
            label = key_map.get(k, k.replace("_", " ").title())

            if k == "printers" and isinstance(v, dict):
                # Render aliases as a sub-list
                v = ", ".join([f"{name} ({addr})" for name, addr in v.items()]) or "(none)"
            table.add_row(label, str(v))
        console.print(table)
    else:
        console.print(data)

def print_error(message: str):
    console.print(f"[bold red]Error:[/bold red] {message}")