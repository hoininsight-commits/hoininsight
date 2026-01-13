from datetime import datetime
from src.utils.paths import ensure_dirs, REPORTS_DIR

def main():
    ensure_dirs()
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS_DIR / f"_report_stub_{stamp}.md"
    out.write_text("# Daily Brief (stub)\n", encoding="utf-8")

if __name__ == "__main__":
    main()
