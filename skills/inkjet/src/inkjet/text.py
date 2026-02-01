import os
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

def get_font(size: int = 24, font_name: str = "Helvetica"):
    """Try to load a readable font, fallback to default."""
    candidates = [
        f"/System/Library/Fonts/{font_name}.ttc",
        f"/Library/Fonts/{font_name}.ttf",
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        f"C:\\Windows\\Fonts\\{font_name.lower()}.ttf",
    ]
    
    for path in candidates:
        if os.path.exists(path):
            try:
                return PIL.ImageFont.truetype(path, size)
            except Exception:
                continue
    
    return PIL.ImageFont.load_default()

def render_text(
    text: str,
    size: int = 24,
    font_name: str = "Helvetica",
    width: int = 384,
    padding_left: int = 20,
    padding_top: int = 10,
    line_spacing: int = 8,
    align: str = "left",
) -> PIL.Image.Image:
    """Renders a string (handling multiple lines) to a PIL Image."""
    font = get_font(size, font_name)
    lines = text.split("\n")

    # Process lines to get total height and max width
    dummy = PIL.Image.new("RGB", (width, 1))
    draw = PIL.ImageDraw.Draw(dummy)

    line_metrics = []
    total_h = padding_top * 2
    max_w = 0

    for line in lines:
        if not line.strip():
            # Empty line height
            h = size
            w = 0
        else:
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
            except Exception:
                w, h = draw.textsize(line, font=font)

        line_metrics.append((line, w, h))
        total_h += h + line_spacing
        max_w = max(max_w, w)

    image = PIL.Image.new("RGB", (width, total_h), (255, 255, 255))
    draw = PIL.ImageDraw.Draw(image)

    current_y = padding_top
    for line, w, h in line_metrics:
        # Handle alignment
        if align == "center":
            x = (width - w) // 2
        elif align == "right":
            x = width - w - padding_left
        else:  # left
            x = padding_left

        draw.text((x, current_y), line, fill=(0, 0, 0), font=font)
        current_y += h + line_spacing

    return image


def render_markdown(
    content: str,
    size: int = 18,
    width: int = 384,
    padding_left: int = 0,
    padding_top: int = 10,
    line_spacing: int = 8,
    align: str = "left",
) -> PIL.Image.Image:
    """Renders markdown content to a PIL Image using Rich's layout engine."""
    from rich.console import Console
    from rich.markdown import Markdown
    import io
    import re

    # Calculate character width based on available space and mono font size
    # Typical mono fonts are ~0.6x the height in width.
    char_width_px = size * 0.6
    console_width = max(20, int((width - (padding_left * 2)) // char_width_px))

    # Thermal printers are narrow.
    # We use a no-color console to avoid ANSI codes in the bitmap.
    console = Console(
        width=console_width,
        file=io.StringIO(),
        force_terminal=False,
        color_system=None,
        highlight=False,
    )
    md = Markdown(content)
    console.print(md)
    output = console.file.getvalue()

    # Strip any remaining ANSI escape sequences just in case
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    output = ansi_escape.sub("", output)

    # Use a monospaced font for predictable markdown layout
    return render_text(
        output.strip("\n"),
        size=size,
        font_name="Courier",
        width=width,
        padding_left=padding_left,
        padding_top=padding_top,
        line_spacing=line_spacing,
        align=align,
    )
