
import csv
import json
import os
from pathlib import Path
from datetime import datetime

def main():
    base_dir = Path("data/curated")
    # Date range: This week (taking from Sunday Jan 18th or Monday Jan 19th)
    # User said "this week", let's include last few days.
    start_date_str = "2026-01-19"
    
    aggregated_data = {}
    
    print(f"Scanning {base_dir} for data since {start_date_str}...")

    file_count = 0
    
    for csv_file in base_dir.rglob("*.csv"):
        try:
            relative_name = str(csv_file.relative_to(base_dir)).replace(".csv", "").replace("/", "_")
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = []
                for row in reader:
                    # Find date column
                    keys = ['date', 'Date', 'timestamp', 'ts_utc']
                    date_val = None
                    for k in keys:
                        if k in row:
                            date_val = row[k]
                            break
                            
                    if not date_val:
                        continue
                        
                    if date_val >= start_date_str:
                        rows.append(row)
                
                if rows:
                    aggregated_data[relative_name] = rows
                    print(f"  - {relative_name}: {len(rows)} rows")
                    file_count += 1
                    
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")

    # Output file
    downloads_dir = Path(os.path.expanduser("~/Downloads"))
    if not downloads_dir.exists():
        print(f"Downloads dir {downloads_dir} not found, saving to local dir.")
        output_path = Path("hoin_weekly_data_2026_01_23.json")
    else:
        output_path = downloads_dir / "hoin_weekly_data_2026_01_23.json"

    # Also aggregate anomalies
    anomalies_dir = Path("data/features/anomalies/2026/01")
    anomalies_data = {}
    
    print(f"Scanning {anomalies_dir} for anomalies since {start_date_str}...")
    
    if anomalies_dir.exists():
        for day_dir in anomalies_dir.iterdir():
            if not day_dir.is_dir(): continue
            
            # Check if day is within range
            day_str = f"2026-01-{day_dir.name}"
            if day_str < start_date_str:
                continue
                
            anomalies_data[day_str] = {}
            for json_file in day_dir.glob("*.json"):
                try:
                    content = json.loads(json_file.read_text(encoding='utf-8'))
                    anomalies_data[day_str][json_file.stem] = content
                except Exception as e:
                    print(f"Error reading {json_file}: {e}")

    final_output = {
        "raw_values": aggregated_data,
        "anomalies_detected": anomalies_data
    }
        
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
        
    print(f"\nSuccessfully aggregated {file_count} raw datasets and {len(anomalies_data)} days of anomalies.")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    main()
