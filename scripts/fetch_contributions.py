import requests
from bs4 import BeautifulSoup
import json
import re
import os
import sys

def fetch_contributions(username="vatsalgargg", output_json="data/contributions.json"):
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching contributions from {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
    except Exception as e:
        print(f"Network error fetching contributions: {e}")
        # If output file already exists, keep it or exit
        if os.path.exists(output_json):
            print("Using existing local contributions data as fallback.")
            return
        sys.exit(1)
        
    if response.status_code != 200:
        print(f"Error fetching contributions: HTTP {response.status_code}")
        if os.path.exists(output_json):
            print("Using existing local contributions data as fallback.")
            return
        sys.exit(1)
        
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Locate all day elements in the calendar
    # In GitHub's calendar, days are typically <rect> (SVG calendar) or <td> elements with class "ContributionCalendar-day"
    days = soup.find_all(attrs={"data-date": True})
    
    if not days:
        print("Warning: No elements with 'data-date' found. Attempting backup parsing...")
        # Check if they are inside tooltips
        
    # Map tooltip text by the element id it belongs to
    tooltips = {}
    for tt in soup.find_all("tool-tip"):
        for_id = tt.get("for")
        if for_id:
            tooltips[for_id] = tt.get_text().strip()
            
    # Process each day
    parsed_days = []
    total_contributions = 0
    best_day_count = 0
    best_day_date = ""
    
    for day in days:
        date_str = day.get("data-date")
        level_str = day.get("data-level", "0")
        day_id = day.get("id")
        
        # Parse contribution count from the tooltip
        count = 0
        tt_text = tooltips.get(day_id, "") if day_id else ""
        
        if tt_text:
            # Regex to match counts: "12 contributions on March 1, 2026" or "1 contribution..."
            match = re.search(r"(\d+)\s+contribution", tt_text)
            if match:
                count = int(match.group(1))
            elif "No contribution" in tt_text or "no contribution" in tt_text:
                count = 0
        else:
            # Fallback if no tooltip found: infer from data-level
            # Level 0 = 0, Level 1 = 1-2, Level 2 = 3-5, Level 3 = 6-8, Level 4 = 9+
            level = int(level_str)
            if level == 0:
                count = 0
            elif level == 1:
                count = 1
            elif level == 2:
                count = 3
            elif level == 3:
                count = 6
            elif level == 4:
                count = 10
                
        parsed_days.append({
            "date": date_str,
            "level": int(level_str),
            "count": count
        })
        
    # Sort days chronologically
    parsed_days.sort(key=lambda x: x["date"])
    
    if not parsed_days:
        print("Error: Failed to parse any contribution days. Exiting.")
        sys.exit(1)
        
    # Calculate statistics
    longest_streak = 0
    temp_streak = 0
    for day in parsed_days:
        count = day["count"]
        total_contributions += count
        
        if count > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0
            
        if count > best_day_count:
            best_day_count = count
            best_day_date = day["date"]
            
    # Calculate current streak by scanning backward
    current_streak = 0
    reversed_days = list(reversed(parsed_days))
    
    # We find if there is an active streak (has contributions within last 2 days)
    streak_active = False
    start_idx = 0
    for idx, day in enumerate(reversed_days[:3]):
        if day["count"] > 0:
            streak_active = True
            start_idx = idx
            break
            
    if streak_active:
        for day in reversed_days[start_idx:]:
            if day["count"] > 0:
                current_streak += 1
            else:
                break
    else:
        current_streak = 0
        
    result = {
        "username": username,
        "total_contributions": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": {
            "date": best_day_date,
            "count": best_day_count
        },
        "days": parsed_days
    }
    
    # Save the JSON data
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        
    print(f"Successfully fetched and parsed {len(parsed_days)} days of contributions.")
    print(f"Total contributions: {total_contributions}")
    print(f"Current streak: {current_streak} days, Longest streak: {longest_streak} days")
    print(f"Best day: {best_day_date} ({best_day_count} contributions)")

if __name__ == "__main__":
    uname = sys.argv[1] if len(sys.argv) > 1 else "vatsalgargg"
    fetch_contributions(uname)
