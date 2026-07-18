import os
import sys

def make_info_card(output_svg_path="info-card.svg"):
    # Dimensions of the SVG
    width = 490
    height = 360
    
    # Define the Neofetch rows
    # Each row is a tuple: (Key, Value, Icon)
    rows = [
        ("OS", "Garuda Linux / Arch Linux", "󰣇"),
        ("Host", "vatsal.works", ""),
        ("Kernel", "Profile README v2.0", ""),
        ("Uptime", "TryHackMe: mrR0bOt", "󰥔"),
        ("Shell", "zsh (active-threat-hunter)", ""),
        ("Stack", "Python, Git, OSINT, Security, C/C++", ""),
        ("Projects", "github.com/vatsalgargg", "")
    ]
    
    # SMIL Animation parameters
    line_delay = 0.25 # Stagger delay between lines
    start_offset = 0.5 # Start after some initial buffer
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%">')
    
    # Styles
    svg.append('  <style>')
    svg.append('    .card-bg {')
    svg.append('      fill: #0d1117;')
    svg.append('      stroke: #30363d;')
    svg.append('      stroke-width: 1.5;')
    svg.append('    }')
    svg.append('    .title-text {')
    svg.append('      font-family: "Fira Code", "Consolas", "Courier New", monospace;')
    svg.append('      font-size: 16px;')
    svg.append('      font-weight: bold;')
    svg.append('      fill: #1ED760;')
    svg.append('    }')
    svg.append('    .host-text {')
    svg.append('      font-family: "Fira Code", "Consolas", "Courier New", monospace;')
    svg.append('      font-size: 16px;')
    svg.append('      font-weight: bold;')
    svg.append('      fill: #8b949e;')
    svg.append('    }')
    svg.append('    .sep-text {')
    svg.append('      font-family: "Fira Code", "Consolas", "Courier New", monospace;')
    svg.append('      font-size: 14px;')
    svg.append('      fill: #30363d;')
    svg.append('    }')
    svg.append('    .key-text {')
    svg.append('      font-family: "Fira Code", "Consolas", "Courier New", monospace;')
    svg.append('      font-size: 13px;')
    svg.append('      font-weight: bold;')
    svg.append('      fill: #1ED760;')
    svg.append('    }')
    svg.append('    .val-text {')
    svg.append('      font-family: "Fira Code", "Consolas", "Courier New", monospace;')
    svg.append('      font-size: 13px;')
    svg.append('      fill: #c9d1d9;')
    svg.append('    }')
    svg.append('    .fade-in {')
    svg.append('      opacity: 0;')
    svg.append('    }')
    svg.append('  </style>')
    
    # Card Background
    svg.append(f'  <rect width="{width}" height="{height}" class="card-bg" rx="8" />')
    
    # Terminal Top Bar
    # Window controls (Red, Yellow, Green circles)
    svg.append('  <!-- Terminal controls -->')
    svg.append('  <circle cx="25" cy="20" r="6" fill="#ff5f56" />')
    svg.append('  <circle cx="45" cy="20" r="6" fill="#ffbd2e" />')
    svg.append('  <circle cx="65" cy="20" r="6" fill="#27c93f" />')
    svg.append('  <text x="245" y="24" font-family="Fira Code, Consolas, monospace" font-size="11" fill="#8b949e" text-anchor="middle">neofetch --vatsal</text>')
    svg.append('  <line x1="0" y1="36" x2="490" y2="36" stroke="#30363d" stroke-width="1" />')
    
    # Content Group
    y_start = 75
    y_gap = 25
    
    # Title Line: vatsal@github
    title_start = start_offset
    svg.append(f'  <g class="fade-in" opacity="0">')
    svg.append(f'    <text x="25" y="{y_start}" class="title-text">vatsal</text>')
    svg.append(f'    <text x="80" y="{y_start}" class="host-text">@github</text>')
    svg.append(f'    <animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{title_start}s" fill="freeze" />')
    svg.append(f'  </g>')
    
    # Separator Line: -------------
    sep_start = title_start + line_delay
    svg.append(f'  <g class="fade-in" opacity="0">')
    svg.append(f'    <text x="25" y="{y_start + 12}" class="sep-text">--------------------------------------</text>')
    svg.append(f'    <animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{sep_start}s" fill="freeze" />')
    svg.append(f'  </g>')
    
    # Info Rows
    current_time = sep_start + line_delay
    for i, (key, val, icon) in enumerate(rows):
        row_y = y_start + 30 + i * y_gap
        svg.append(f'  <g class="fade-in" opacity="0">')
        # We can include an icon or prefix
        svg.append(f'    <text x="25" y="{row_y}" class="key-text">{key}:</text>')
        # Align value text slightly to the right of key
        # Estimate width of key: len(key) * 8px + safety margin
        val_x = 25 + max(len(k[0]) for k in rows) * 8.5 + 20
        svg.append(f'    <text x="{val_x}" y="{row_y}" class="val-text">{val}</text>')
        svg.append(f'    <animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{current_time}s" fill="freeze" />')
        svg.append(f'  </g>')
        current_time += line_delay
        
    # Color Blocks at bottom
    colors = ["#30363d", "#ff5f56", "#1ED760", "#ffbd2e", "#2b91ff", "#ff79c6", "#50fa7b", "#abb2bf"]
    block_y = y_start + 40 + len(rows) * y_gap
    block_x_start = 25
    block_w = 22
    block_h = 16
    
    color_start = current_time
    svg.append(f'  <g class="fade-in" opacity="0">')
    for idx, color in enumerate(colors):
        x = block_x_start + idx * (block_w + 6)
        svg.append(f'    <rect x="{x}" y="{block_y}" width="{block_w}" height="{block_h}" fill="{color}" rx="2" />')
        # Dark variation block below
        svg.append(f'    <rect x="{x}" y="{block_y + 22}" width="{block_w}" height="{block_h}" fill="{color}" opacity="0.6" rx="2" />')
        
    svg.append(f'    <animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{color_start}s" fill="freeze" />')
    svg.append(f'  </g>')
    
    svg.append('</svg>')
    
    with open(output_svg_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))
        
    print(f"Info Card SVG generated at {output_svg_path}")

if __name__ == "__main__":
    make_info_card()
