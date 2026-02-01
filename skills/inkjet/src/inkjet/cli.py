"""inkjet CLI — Bluetooth thermal printer control."""
import typer
import sys
import asyncio
from typing import Optional
from typing_extensions import Annotated
from pathlib import Path
import PIL.Image

from .discovery import scan_printers
from .printer import Printer
from .output import console, print_result, print_error
from .config import load_config, update_config, get_config_val
from .text import render_text, render_markdown
from .image import process_image, render_qr

# Main app
app = typer.Typer(
    name="inkjet",
    help="🖨️ Bluetooth thermal printer CLI. Print text, images, QR codes.",
    no_args_is_help=True,
)

def version_callback(value: bool):
    if value:
        from . import __version__
        console.print(f"inkjet v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True),
):
    """
    🖨️ Bluetooth thermal printer CLI. Print text, images, QR codes.
    """
    pass

# Print subcommand group
print_app = typer.Typer(help="Print content to the thermal printer")
app.add_typer(print_app, name="print")

# Config subcommand group
config_app = typer.Typer(help="Manage configuration")
app.add_typer(config_app, name="config")

def resolve_address(address: Optional[str]) -> Optional[str]:
    """Helper to resolve a UUID/MAC from config, alias, or direct input."""
    config = load_config()
    default_addr = config.get("default_printer")
    
    # Explicit 'default' alias
    if address == "default":
        return default_addr

    # If no override, use default
    target = address or default_addr
    if not target:
        return None
        
    # Check if the target is an alias
    aliases = config.get("printers", {})
    if target in aliases:
        return aliases[target]
        
    return target

@app.command()
def scan(
    timeout: Annotated[int, typer.Option("--timeout", "-t", help="Scan timeout in seconds")] = 10,
    json: bool = typer.Option(False, "--json", help="Output in JSON format"),
    local: bool = typer.Option(False, "--local", help="Save discovered printer to local config"),
):
    """Scan for nearby Bluetooth thermal printers."""
    config = load_config()
    default_addr = config.get("default_printer")
    aliases = config.get("printers", {})
    
    # Invert aliases for lookup: {address: [names]}
    from collections import defaultdict
    addr_map = defaultdict(list)
    for name, addr in aliases.items():
        addr_map[addr].append(name)

    with console.status("[bold blue]Scanning for printers...", spinner="dots"):
        devices = asyncio.run(scan_printers(timeout=timeout))
    
    printers = []
    for p in devices:
        found_aliases = addr_map.get(p.address, [])
        if p.address == default_addr:
            found_aliases.insert(0, "default")
        
        printers.append({
            "name": p.name, 
            "address": p.address, 
            "alias": ", ".join(found_aliases) if found_aliases else "--"
        })
    
    print_result({"printers": printers}, json_output=json)
    
    if printers and not get_config_val("default_printer"):
        update_config("default_printer", printers[0]["address"], local=local)
        if not json:
            console.print(f"\nAuto-configured default printer: [magenta]{printers[0]['address']}[/magenta]")

@app.command()
def whoami(json: bool = typer.Option(False, "--json", help="Output in JSON format")):
    """Show current printer configuration."""
    config = load_config()
    print_result(config, json_output=json)

@app.command()
def about():
    """Show project information and credits."""
    from . import __version__
    console.print(f"[bold magenta]inkjet[/bold magenta] v{__version__}")
    console.print("Thermal Printer CLI for Humans and Agents.")
    console.print()
    console.print("Created by: [bold]Aaron Chartier[/bold]")
    console.print("GitHub:     https://github.com/AaronChartier/inkjet")
    console.print()
    console.print("[italic]The physical terminal for agents. Zero ink.[/italic]")

@app.command()
def doctor():
    """Diagnose printer connection issues."""
    from importlib.metadata import version
    from .config import get_config_path
    console.print("\n[bold]inkjet doctor[/bold]\n")
    
    console.print(f"[green]✓[/green] Python {sys.version_info.major}.{sys.version_info.minor}")
    try:
        console.print(f"[green]✓[/green] Bleak {version('bleak')}")
    except Exception:
        console.print("[yellow]![/yellow] Bleak version unknown")
    
    console.print(f"[blue]ℹ[/blue] Active Config: [bold]{get_config_path()}[/bold]")

    if sys.platform == "darwin":
        console.print("[blue]ℹ[/blue] macOS detected: Ensure Bluetooth is [bold]ON[/bold] and [bold]Bluetooth Access[/bold] is allowed in Privacy Settings.")

    addr = get_config_val("default_printer")
    if addr:
        console.print(f"[green]✓[/green] Configured address: {addr}")
    else:
        console.print("[yellow]![/yellow] No printer configured. Run: inkjet scan")

@app.command()
def feed(
    steps: int = typer.Argument(100, help="Number of steps to feed"),
    address: Optional[str] = typer.Option(None, "--address", "-a", help="Printer address or alias override"),
    energy: Optional[int] = typer.Option(None, help="Hardware energy override"),
    speed: Optional[int] = typer.Option(None, help="Hardware speed override"),
    quality: Optional[int] = typer.Option(None, help="Hardware quality override"),
):
    """Feed paper forward."""
    addr = resolve_address(address)
    if not addr:
        print_error("No printer configured.")
        raise typer.Exit(1)

    async def do_feed():
        printer = Printer(
            addr,
            energy=energy or get_config_val("energy"),
            speed=speed or get_config_val("print_speed"),
            quality=quality or get_config_val("quality"),
        )
        await printer.connect()
        await printer.feed(steps)
        await printer.disconnect()

    with console.status(f"[blue]Feeding {steps} steps..."):
        asyncio.run(do_feed())
    console.print(f"[green]✓[/green] Fed {steps} steps")

# Print subcommands
@print_app.command("text")
def print_text(
    text: Annotated[str, typer.Argument(help="Text to print (use '-' for stdin)")],
    size: Optional[int] = typer.Option(None, "--size", "-s", help="Font size"),
    font: str = typer.Option("Helvetica", "--font", "-f", help="Font name"),
    markdown: bool = typer.Option(False, "--markdown", "-m", help="Render input as Markdown"),
    address: Optional[str] = typer.Option(None, "--address", "-a", help="Printer address or alias override"),
    # Layout overrides
    align: Optional[str] = typer.Option(None, help="Text alignment (left, center, right)"),
    padding_left: Optional[int] = typer.Option(None, help="Left margin in pixels"),
    padding_top: Optional[int] = typer.Option(None, help="Top margin in pixels"),
    line_spacing: Optional[int] = typer.Option(None, help="Vertical spacing between lines"),
    # Hardware overrides
    energy: Optional[int] = typer.Option(None, help="Hardware energy override"),
    speed: Optional[int] = typer.Option(None, help="Hardware speed override"),
    quality: Optional[int] = typer.Option(None, help="Hardware quality override"),
):
    """Print text or markdown to the thermal printer."""
    addr = resolve_address(address)
    if not addr:
        print_error("No printer configured.")
        raise typer.Exit(1)

    if text == "-":
        text = sys.stdin.read().strip()

    # Apply escape character handling so \n becomes a real newline
    try:
        text = text.encode('utf-8').decode('unicode_escape')
    except Exception:
        pass

    if markdown:
        image = render_markdown(
            text,
            size=size or get_config_val("font_size"),
            padding_left=padding_left if padding_left is not None else get_config_val("padding_left"),
            padding_top=padding_top if padding_top is not None else get_config_val("padding_top"),
            line_spacing=line_spacing if line_spacing is not None else get_config_val("line_spacing"),
            align=align or get_config_val("align"),
        )
    else:
        image = render_text(
            text,
            size=size or get_config_val("font_size"),
            font_name=font,
            padding_left=padding_left if padding_left is not None else get_config_val("padding_left"),
            padding_top=padding_top if padding_top is not None else get_config_val("padding_top"),
            line_spacing=line_spacing if line_spacing is not None else get_config_val("line_spacing"),
            align=align or get_config_val("align"),
        )

    async def do_print():
        printer = Printer(
            addr,
            energy=energy or get_config_val("energy"),
            speed=speed or get_config_val("print_speed"),
            quality=quality or get_config_val("quality"),
        )
        await printer.connect()
        await printer.print_image(image)
        await printer.feed(120)
        await printer.disconnect()

    with console.status("[blue]Printing..."):
        asyncio.run(do_print())
    console.print("[green]✓[/green] Printed!")

@print_app.command("image")
def print_image(
    path: Annotated[str, typer.Argument(help="Image file path (use '-' for stdin)")],
    dither: bool = typer.Option(True, "--dither/--no-dither", "-d", help="Apply dithering"),
    address: Optional[str] = typer.Option(None, "--address", "-a", help="Printer address or alias override"),
    # Hardware overrides
    energy: Optional[int] = typer.Option(None, help="Hardware energy override"),
    speed: Optional[int] = typer.Option(None, help="Hardware speed override"),
    quality: Optional[int] = typer.Option(None, help="Hardware quality override"),
):
    """Print an image file."""
    addr = resolve_address(address)
    if not addr:
        print_error("No printer configured.")
        raise typer.Exit(1)

    try:
        if path == "-":
            img_raw = PIL.Image.open(sys.stdin.buffer)
        else:
            img_raw = PIL.Image.open(path)
        
        img = process_image(img_raw, dither=dither)
        
        async def do_print():
            printer = Printer(
                addr,
                energy=energy or get_config_val("energy"),
                speed=speed or get_config_val("print_speed"),
                quality=quality or get_config_val("quality"),
            )
            await printer.connect()
            await printer.print_image(img)
            await printer.feed(120)
            await printer.disconnect()

        with console.status("[blue]Printing image..."):
            asyncio.run(do_print())
        console.print("[green]✓[/green] Printed image!")
    except Exception as e:
        print_error(f"Failed to print image: {e}")

@print_app.command("qr")
def print_qr(
    data: Annotated[str, typer.Argument(help="Data to encode in QR code")],
    size: int = typer.Option(250, "--size", "-s", help="QR code size in pixels"),
    address: Optional[str] = typer.Option(None, "--address", "-a", help="Printer address or alias override"),
    # Hardware overrides
    energy: Optional[int] = typer.Option(None, help="Hardware energy override"),
    speed: Optional[int] = typer.Option(None, help="Hardware speed override"),
    quality: Optional[int] = typer.Option(None, help="Hardware quality override"),
):
    """Print a QR code."""
    addr = resolve_address(address)
    if not addr:
        print_error("No printer configured.")
        raise typer.Exit(1)

    img = render_qr(data, size=size)
    
    async def do_print():
        printer = Printer(
            addr,
            energy=energy or get_config_val("energy"),
            speed=speed or get_config_val("print_speed"),
            quality=quality or get_config_val("quality"),
        )
        await printer.connect()
        await printer.print_image(img)
        await printer.feed(120)
        await printer.disconnect()

    with console.status("[blue]Printing QR code..."):
        asyncio.run(do_print())
    console.print("[green]✓[/green] Printed QR code!")

@print_app.command("file")
def print_file(
    path: Annotated[str, typer.Argument(help="Path to text or markdown file")],
    size: Optional[int] = typer.Option(None, "--size", "-s", help="Font size"),
    font: str = typer.Option("Helvetica", "--font", "-f", help="Font name"),
    address: Optional[str] = typer.Option(None, "--address", "-a", help="Printer address or alias override"),
    # Layout overrides
    align: Optional[str] = typer.Option(None, help="Text alignment (left, center, right)"),
    padding_left: Optional[int] = typer.Option(None, help="Left margin in pixels"),
    padding_top: Optional[int] = typer.Option(None, help="Top margin in pixels"),
    line_spacing: Optional[int] = typer.Option(None, help="Vertical spacing between lines"),
    # Hardware overrides
    energy: Optional[int] = typer.Option(None, help="Hardware energy override"),
    speed: Optional[int] = typer.Option(None, help="Hardware speed override"),
    quality: Optional[int] = typer.Option(None, help="Hardware quality override"),
):
    """Print the contents of a text file."""
    addr = resolve_address(address)
    if not addr:
        print_error("No printer configured.")
        raise typer.Exit(1)

    try:
        with open(path, "r") as f:
            content = f.read().strip()
        
        # Apply escape character handling
        try:
            content = content.encode('utf-8').decode('unicode_escape')
        except Exception:
            pass

        if path.endswith(".md"):
            img = render_markdown(
                content,
                size=size or get_config_val("font_size"),
                padding_left=padding_left if padding_left is not None else get_config_val("padding_left"),
                padding_top=padding_top if padding_top is not None else get_config_val("padding_top"),
                line_spacing=line_spacing if line_spacing is not None else get_config_val("line_spacing"),
                align=align or get_config_val("align"),
            )
        else:
            img = render_text(
                content,
                size=size or get_config_val("font_size"),
                font_name=font,
                padding_left=padding_left if padding_left is not None else get_config_val("padding_left"),
                padding_top=padding_top if padding_top is not None else get_config_val("padding_top"),
                line_spacing=line_spacing if line_spacing is not None else get_config_val("line_spacing"),
                align=align or get_config_val("align"),
            )
        
        async def do_print():
            printer = Printer(
                addr,
                energy=energy or get_config_val("energy"),
                speed=speed or get_config_val("print_speed"),
                quality=quality or get_config_val("quality"),
            )
            await printer.connect()
            await printer.print_image(img)
            await printer.feed(120)
            await printer.disconnect()

        with console.status(f"[blue]Printing {path}..."):
            asyncio.run(do_print())
        console.print(f"[green]✓[/green] Printed {path}!")
    except Exception as e:
        print_error(f"Failed to print file: {e}")

# Config subcommands
@config_app.command("show")
def config_show(json: bool = typer.Option(False, "--json", help="Output in JSON format")):
    """Show all configuration values."""
    print_result(load_config(), json_output=json)

@config_app.command("set")
def config_set(
    key: str, 
    value: str,
    local: bool = typer.Option(False, "--local", help="Force saving to local .inkjet/ folder")
):
    """Update a configuration value."""
    # Mapping for human-friendly shortcuts
    key_map = {
        "printer": "default_printer"
    }
    target_key = key_map.get(key, key)

    if value.isdigit():
        val = int(value)
    else:
        val = value
    update_config(target_key, val, local=local)
    console.print(f"[green]✓[/green] Updated {target_key} to {val} ({'local' if local else 'hybrid'})")

@config_app.command("alias")
def config_alias(
    name: str, 
    address: str,
    local: bool = typer.Option(False, "--local", help="Force saving to local .inkjet/ folder")
):
    """Save a printer address with a friendly name."""
    config = load_config()
    printers = config.get("printers", {})
    printers[name] = address
    update_config("printers", printers, local=local)
    console.print(f"[green]✓[/green] Alias saved: [bold]{name}[/bold] -> {address} ({'local' if local else 'hybrid'})")

if __name__ == "__main__":
    app()