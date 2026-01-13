from pathlib import Path
from datetime import datetime
from src.topic_selectors.simple_topic import select_topics

def main():
    # anomalies 경로는 오늘 UTC 기준 폴더를 사용
    y = datetime.utcnow().strftime("%Y")
    m = datetime.utcnow().strftime("%m")
    d = datetime.utcnow().strftime("%d")
    anomalies_path = Path(".") / "data" / "features" / "anomalies" / y / m / d / "anomalies.json"
    select_topics(Path("."), anomalies_path)

if __name__ == "__main__":
    main()
