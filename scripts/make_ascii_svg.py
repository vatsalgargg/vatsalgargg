import os
import sys
import html
from PIL import Image, ImageDraw

# Character ramp from bright to dark
RAMP = " .':-=+*cs#%@"

def create_placeholder_prepped_image(path):
    print("No source photo found. Creating a stylized hacker avatar placeholder...")
    # Create a 400x400 grayscale image (white background)
    img = Image.new("L", (400, 400), 255)
    draw = ImageDraw.Draw(img)
    
    # Draw a stylized hacker silhouette
    # Shoulders
    draw.chord([50, 220, 350, 450], 0, 360, fill=80)
    # Head
    draw.ellipse([120, 80, 280, 240], fill=40)
    # Hood / Cap
    draw.polygon([(110, 110), (200, 50), (290, 110), (200, 140)], fill=20)
    # Glasses
    draw.rectangle([150, 140, 190, 165], fill=220)
    draw.rectangle([210, 140, 250, 165], fill=220)
    draw.line([190, 152, 210, 152], fill=220, width=4)
    # Binary code lines on background
    for y in range(20, 380, 40):
        draw.text((20, y), "101011001", fill=180)
        draw.text((300, y), "011010010", fill=180)
        
    img.save(path)

def make_ascii_svg(image_path="source-prepped.png", output_svg_path="vatsal-ascii.svg"):
    if not os.path.exists(image_path):
        # Check if source-photo.jpg exists and prep it
        if os.path.exists("source-photo.jpg"):
            print("Found source-photo.jpg. Prepping photo first...")
            from prep_photo import prep_photo_with_fallback
            prep_photo_with_fallback("source-photo.jpg", image_path)
        else:
            create_placeholder_prepped_image(image_path)
            
    # Load the prepped image
    try:
        img = Image.open(image_path).convert("L")
    except Exception as e:
        print(f"Error opening image: {e}")
        sys.exit(1)
        
    # Standard grid size: 100 columns
    cols = 100
    aspect_ratio = img.height / img.width
    # Character aspect ratio is roughly 0.6 width / 1.0 height. 
    # To prevent stretching, we adjust rows by multiplying by character aspect ratio.
    rows = int(cols * aspect_ratio * 0.55)
    
    # Resize image to characters grid
    img_resized = img.resize((cols, rows), Image.Resampling.LANCZOS)
    
    # Generate ASCII
    ascii_rows = []
    for y in range(rows):
        row_str = ""
        for x in range(cols):
            val = img_resized.getpixel((x, y))
            # Map 0-255 to 0-(len(RAMP)-1)
            # 255 (white) should map to space (index 0)
            # 0 (black) should map to @ (index len(RAMP)-1)
            idx = int((255 - val) / 255 * (len(RAMP) - 1))
            row_str += RAMP[idx]
        # HTML escape characters to prevent SVG rendering issues
        ascii_rows.append(html.escape(row_str))
        
    # Layout dimensions
    char_w = 7.2
    char_h = 12
    width = int(cols * char_w) + 20
    height = int(rows * char_h) + 20
    
    # Timing
    row_dur = 0.06 # duration per row in seconds
    stagger = 0.04 # delay between rows starting in seconds
    
    # Start building SVG
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%">')
    
    # Add Stylesheet
    svg.append('  <style>')
    svg.append('    .ascii-text {')
    svg.append('      font-family: "Fira Code", "Consolas", "Courier New", monospace;')
    svg.append('      font-size: 11px;')
    svg.append('      fill: #1ED760;')
    svg.append('      font-weight: bold;')
    svg.append('    }')
    svg.append('    .cursor {')
    svg.append('      fill: #1ED760;')
    svg.append('    }')
    svg.append('    .bg {')
    svg.append('      fill: #0d1117;')
    svg.append('    }')
    svg.append('  </style>')
    
    # Background
    svg.append(f'  <rect width="100%" height="100%" class="bg" rx="8" />')
    
    # Clip paths for row reveals
    svg.append('  <defs>')
    for i in range(rows):
        start_time = round(i * stagger, 3)
        svg.append(f'    <clipPath id="clip-row-{i}">')
        svg.append(f'      <rect x="10" y="{10 + i * char_h}" width="0" height="{char_h + 2}">')
        svg.append(f'        <animate attributeName="width" from="0" to="{cols * char_w}" dur="{row_dur}s" begin="{start_time}s" fill="freeze" />')
        svg.append(f'      </rect>')
        svg.append(f'    </clipPath>')
    svg.append('  </defs>')
    
    # Group containing text
    svg.append('  <g class="ascii-text">')
    for i, row in enumerate(ascii_rows):
        # Render the text line clipped by the respective clipPath
        svg.append(f'    <text x="10" y="{20 + i * char_h}" clip-path="url(#clip-row-{i})">{row}</text>')
    svg.append('  </g>')
    
    # Cursors for typing reveal
    for i in range(rows):
        start_time = round(i * stagger, 3)
        # Animate the cursor along the width of the row, then fade it out
        svg.append(f'  <rect class="cursor" x="10" y="{11 + i * char_h}" width="{char_w}" height="{char_h - 1}" opacity="0">')
        svg.append(f'    <animate attributeName="x" from="10" to="{10 + cols * char_w}" dur="{row_dur}s" begin="{start_time}s" fill="freeze" />')
        svg.append(f'    <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.99;1" dur="{row_dur}s" begin="{start_time}s" fill="freeze" />')
        svg.append(f'  </rect>')
        
    # Add a final blinking terminal cursor at the end of the text
    last_row_start_x = 10 + len(ascii_rows[-1].replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").strip()) * char_w
    last_row_y = 11 + (rows - 1) * char_h
    total_dur = round(rows * stagger + row_dur, 3)
    
    svg.append(f'  <rect class="cursor" x="{last_row_start_x}" y="{last_row_y}" width="{char_w}" height="{char_h - 1}" opacity="0">')
    # Make it visible after the typewriter animation completes
    svg.append(f'    <animate attributeName="opacity" values="1" dur="0.1s" begin="{total_dur}s" fill="freeze" />')
    # Make it blink after it shows up
    svg.append(f'    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite" begin="{total_dur + 0.1}s" />')
    svg.append(f'  </rect>')
    
    svg.append('</svg>')
    
    with open(output_svg_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))
        
    print(f"ASCII SVG generated at {output_svg_path}")

if __name__ == "__main__":
    make_ascii_svg()
