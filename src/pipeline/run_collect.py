from datetime import datetime
from src.utils.paths import ensure_dirs, RAW_DIR

def main():
    ensure_dirs()
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out = RAW_DIR / f"_collect_stub_{stamp}.txt"
    out.write_text("collect stub\n", encoding="utf-8")

if __name__ == "__main__":
    main()
