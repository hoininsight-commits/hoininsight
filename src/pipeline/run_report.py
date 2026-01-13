from pathlib import Path
from datetime import datetime
from src.reporters.daily_report import write_daily_brief

def main():
    y = datetime.utcnow().strftime("%Y")
    m = datetime.utcnow().strftime("%m")
    d = datetime.utcnow().strftime("%d")
    topics_path = Path(".") / "data" / "topics" / y / m / d / "topics.json"
    write_daily_brief(Path("."), topics_path)

if __name__ == "__main__":
    main()
