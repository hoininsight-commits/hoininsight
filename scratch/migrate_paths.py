import os
import shutil
from pathlib import Path

def migrate():
    base_dir = Path("data/scripts")
    if not base_dir.exists():
        print("data/scripts not found")
        return

    # Iterate through YYYYMMDD directories
    for date_dir in base_dir.iterdir():
        if not date_dir.is_dir() or not (len(date_dir.name) == 8 and date_dir.name.isdigit()):
            continue
        
        date_str = date_dir.name
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        
        print(f"Processing {date_str}...")
        
        # Iterate through round directories
        for round_dir in date_dir.iterdir():
            if not round_dir.is_dir():
                continue
            
            round_val = round_dir.name
            new_parent = base_dir / year / month / day / f"Round_{round_val}"
            new_parent.mkdir(parents=True, exist_ok=True)
            
            # Move files
            for file in round_dir.iterdir():
                if file.is_file():
                    target_path = new_parent / file.name
                    print(f"  Moving {file} -> {target_path}")
                    shutil.move(str(file), str(target_path))
            
            # Remove empty round dir
            try:
                round_dir.rmdir()
            except:
                pass
                
        # Remove empty date dir
        try:
            date_dir.rmdir()
        except:
            pass

    # Also check data/signals and data/analysis if they follow same pattern
    for target in ["signals", "analysis"]:
        target_base = Path("data") / target
        if not target_base.exists(): continue
        
        print(f"Processing {target}...")
        for date_dir in target_base.iterdir():
            if not date_dir.is_dir() or not (len(date_dir.name) == 8 and date_dir.name.isdigit()):
                continue
            
            date_str = date_dir.name
            year = date_str[:4]
            month = date_str[4:6]
            day = date_str[6:8]
            
            for round_dir in date_dir.iterdir():
                if not round_dir.is_dir(): continue
                round_val = round_dir.name
                new_parent = target_base / year / month / day / f"Round_{round_val}"
                new_parent.mkdir(parents=True, exist_ok=True)
                for file in round_dir.iterdir():
                    if file.is_file():
                        shutil.move(str(file), str(new_parent / file.name))
                try: round_dir.rmdir()
                except: pass
            try: date_dir.rmdir()
            except: pass

if __name__ == "__main__":
    migrate()
