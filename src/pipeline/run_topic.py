from datetime import datetime
from src.utils.paths import ensure_dirs, TOPICS_DIR

def main():
    ensure_dirs()
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out = TOPICS_DIR / f"_topic_stub_{stamp}.txt"
    out.write_text("topic stub\n", encoding="utf-8")

if __name__ == "__main__":
    main()
