"""
Icon Generator for AntiBanana Chrome Extension
Run this script to generate icon files: python generate_icons.py
Requires: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size):
    """Create an icon with gradient background and banana emoji"""
    # Create image with gradient
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background (purple to blue)
    for y in range(size):
        r = int(102 + (118 - 102) * y / size)
        g = int(126 + (75 - 126) * y / size)
        b = int(234 + (162 - 234) * y / size)
        draw.rectangle([(0, y), (size, y+1)], fill=(r, g, b, 255))
    
    # Draw banana text (using unicode)
    try:
        font_size = int(size * 0.5)
        # Try to use a font that supports emoji
        font = ImageFont.truetype("seguiemj.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw banana emoji or text
    text = "🍌"
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # Draw shield circle (anti-deepfake protection indicator)
    circle_radius = int(size * 0.35)
    circle_center = (size // 2, size // 2)
    draw.ellipse(
        [
            circle_center[0] - circle_radius,
            circle_center[1] - circle_radius,
            circle_center[0] + circle_radius,
            circle_center[1] + circle_radius
        ],
        outline=(255, 255, 255, 128),
        width=max(2, size // 16)
    )
    
    return img

def main():
    """Generate all required icon sizes"""
    sizes = [16, 48, 128]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    for size in sizes:
        icon = create_icon(size)
        filename = f"icon{size}.png"
        filepath = os.path.join(script_dir, filename)
        icon.save(filepath, 'PNG')
        print(f"✓ Generated {filename}")
    
    print("\n✅ All icons generated successfully!")
    print("Icons are ready in the 'icons' folder.")

if __name__ == "__main__":
    main()
