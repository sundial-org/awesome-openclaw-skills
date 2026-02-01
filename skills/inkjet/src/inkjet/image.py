import PIL.Image
import PIL.ImageOps
import qrcode

def process_image(image: PIL.Image.Image, width: int = 384, dither: bool = True) -> PIL.Image.Image:
    """Prepares an image for thermal printing."""
    # Convert to grayscale
    img = image.convert("L")
    
    # Resize to fit printer width while maintaining aspect ratio
    aspect = img.height / img.width
    new_height = int(width * aspect)
    img = img.resize((width, new_height), PIL.Image.Resampling.LANCZOS)
    
    # Apply dithering if requested, otherwise threshold
    if dither:
        img = img.convert("1", dither=PIL.Image.FLOYDSTEINBERG)
    else:
        # Simple thresholding
        img = img.point(lambda x: 0 if x < 128 else 255, mode="1")
        
    # Convert back to RGB as the printer lib expects RGB and does its own conversion to bits
    return img.convert("RGB")

def render_qr(data: str, size: int = 250, width: int = 384) -> PIL.Image.Image:
    """Generates a QR code image."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
    # Resize to requested size
    qr_img = qr_img.resize((size, size), PIL.Image.Resampling.NEAREST)
    
    # Create background of printer width
    final_img = PIL.Image.new("RGB", (width, size), (255, 255, 255))
    x_pos = (width - size) // 2
    final_img.paste(qr_img, (x_pos, 0))
    
    return final_img