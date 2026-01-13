from datetime import datetime
from src.utils.paths import ensure_dirs, CURATED_DIR

def main():
    ensure_dirs()
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out = CURATED_DIR / f"_normalize_stub_{stamp}.txt"
    out.write_text("normalize stub\n", encoding="utf-8")

if __name__ == "__main__":
    main()
