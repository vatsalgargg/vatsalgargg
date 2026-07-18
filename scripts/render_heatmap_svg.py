import json
import os
import sys
from datetime import datetime

# GitHub-like green colors for levels 0 to 4 (and top end neon 5)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

def render_heatmap_svg(json_path="data/contributions.json", output_svg_path="contrib-heatmap.svg"):
    if not os.path.exists(json_path):
        print(f"Error: JSON data file {json_path} does not exist. Run fetch_contributions.py first.")
        sys.exit(1)
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    username = data.get("username", "vatsalgargg")
    total_contribs = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    days = data.get("days", [])
    
    # Grid configuration
    box_size = 11
    box_gap = 3
    grid_x_start = 40
    grid_y_start = 40
    step = box_size + box_gap # 14px
    
    # Outer dimensions
    width = 860
    height = 200
    
    # We have 53 weeks (columns) and 7 days (rows)
    # Let's map days to columns
    # In GitHub's calendar, the grid has 53 columns.
    # We can assign each day to a column based on its index
    # Since days list is chronological:
    # Let's group them into 53 weeks
    weeks = [[] for _ in range(53)]
    
    # To align correctly with days of week, we find the day-of-week of the first day
    # Or we can just build columns of size 7 starting from Sunday or the first day
    # Let's chunk the days into weeks of size 7. 
    # If the first day is not Sunday (day-of-week 0), we can pad the first week
    # Let's do a simple padding:
    if days:
        first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d")
        # weekday() returns 0 for Monday, 6 for Sunday
        # Let's map to Sunday=0, Monday=1 ... Saturday=6
        first_wday = (first_date.weekday() + 1) % 7
        
        # Pad the beginning of the first week
        padded_days = [{"level": 0, "count": 0, "date": "", "padded": True}] * first_wday + days
    else:
        padded_days = []
        
    # Group into columns
    columns = []
    for i in range(0, len(padded_days), 7):
        columns.append(padded_days[i:i+7])
        
    # Keep only the last 53 columns to fit in the card
    columns = columns[-53:]
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%">')
    
    # Stylesheet
    svg.append('  <style>')
    svg.append('    .bg { fill: #0d1117; stroke: #30363d; stroke-width: 1.5; }')
    svg.append('    .label-text { font-family: "Fira Code", "Consolas", "Courier New", monospace; font-size: 10px; fill: #8b949e; }')
    svg.append('    .header-text { font-family: "Fira Code", "Consolas", "Courier New", monospace; font-size: 14px; font-weight: bold; fill: #1ED760; }')
    svg.append('    .stats-text { font-family: "Fira Code", "Consolas", "Courier New", monospace; font-size: 11px; fill: #8b949e; }')
    svg.append('    .stats-highlight { fill: #1ED760; font-weight: bold; }')
    svg.append('    .legend-text { font-family: "Fira Code", "Consolas", "Courier New", monospace; font-size: 9px; fill: #8b949e; }')
    svg.append('  </style>')
    
    # Card Background
    svg.append(f'  <rect width="{width}" height="{height}" class="bg" rx="8" />')
    
    # Title Bar
    svg.append(f'  <text x="25" y="25" class="header-text">vatsal@github ~ $ ./contributions.sh</text>')
    
    # Day labels (Mon, Wed, Fri) on the left
    day_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for r, label in day_labels.items():
        y_pos = grid_y_start + r * step + 9
        svg.append(f'  <text x="12" y="{y_pos}" class="label-text">{label}</text>')
        
    # Render Month labels & cells
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    last_month = -1
    
    for c_idx, col in enumerate(columns):
        x_pos = grid_x_start + c_idx * step
        
        # Check if we should write a month label
        valid_days = [d for d in col if d.get("date") and not d.get("padded")]
        if valid_days:
            first_day_date = datetime.strptime(valid_days[0]["date"], "%Y-%m-%d")
            c_month = first_day_date.month
            if c_month != last_month:
                # Avoid printing month label on the first column to prevent clipping if it's too close to left
                # Space month labels by at least 2 columns
                if c_idx > 1:
                    m_label = month_names[c_month - 1]
                    svg.append(f'  <text x="{x_pos}" y="{grid_y_start - 8}" class="label-text">{m_label}</text>')
                    last_month = c_month
                    
        # Draw cells in this column
        for r_idx, day_info in enumerate(col):
            if r_idx >= 7:
                break
                
            y_pos = grid_y_start + r_idx * step
            
            # If cell is padded (from previous year), draw transparent or darker background
            if day_info.get("padded"):
                fill_color = "transparent"
            else:
                level = day_info.get("level", 0)
                # Cap level to PALETTE length
                level = min(max(0, level), len(PALETTE) - 1)
                fill_color = PALETTE[level]
                
            if fill_color != "transparent":
                # Stagger delay based on diagonal coordinates: col + row
                delay = round((c_idx + r_idx) * 0.015, 3)
                
                # Group with transform for translation animation
                svg.append(f'  <g>')
                svg.append(f'    <rect x="{x_pos}" y="{y_pos}" width="{box_size}" height="{box_size}" rx="2" fill="{fill_color}" opacity="0">')
                # Fade in
                svg.append(f'      <animate attributeName="opacity" from="0" to="1" dur="0.25s" begin="{delay}s" fill="freeze" />')
                # Slide down-right slightly
                svg.append(f'      <animateTransform attributeName="transform" type="translate" from="-4,-4" to="0,0" dur="0.25s" begin="{delay}s" fill="freeze" additive="sum" />')
                svg.append(f'    </rect>')
                svg.append(f'  </g>')
                
    # Footer Stats (Left) & Legend (Right)
    footer_y = grid_y_start + 7 * step + 22
    
    # Stats Text
    svg.append(f'  <text x="25" y="{footer_y}" class="stats-text">')
    svg.append(f'    Total Contributions: <tspan class="stats-highlight">{total_contribs:,}</tspan>  |  ')
    svg.append(f'    Current Streak: <tspan class="stats-highlight">{current_streak} days</tspan>  |  ')
    svg.append(f'    Longest Streak: <tspan class="stats-highlight">{longest_streak} days</tspan>')
    svg.append(f'  </text>')
    
    # Legend: Less -> More
    legend_x_end = grid_x_start + 53 * step - (len(PALETTE) * 14)
    svg.append(f'  <g>')
    svg.append(f'    <text x="{legend_x_end - 32}" y="{footer_y - 2}" class="legend-text">Less</text>')
    for idx, color in enumerate(PALETTE):
        x = legend_x_end + idx * 14
        svg.append(f'    <rect x="{x}" y="{footer_y - 10}" width="10" height="10" rx="1.5" fill="{color}" />')
    svg.append(f'    <text x="{legend_x_end + len(PALETTE)*14 + 6}" y="{footer_y - 2}" class="legend-text">More</text>')
    svg.append(f'  </g>')
    
    svg.append('</svg>')
    
    with open(output_svg_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))
        
    print(f"Heatmap SVG rendered at {output_svg_path}")

if __name__ == "__main__":
    render_heatmap_svg()
