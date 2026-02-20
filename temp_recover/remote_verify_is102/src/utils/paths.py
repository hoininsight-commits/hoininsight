from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CURATED_DIR = DATA_DIR / "curated"
FEATURES_DIR = DATA_DIR / "features"
TOPICS_DIR = DATA_DIR / "topics"
REPORTS_DIR = DATA_DIR / "reports"
ARTIFACTS_DIR = DATA_DIR / "artifacts"

def ensure_dirs():
    for p in [RAW_DIR, CURATED_DIR, FEATURES_DIR, TOPICS_DIR, REPORTS_DIR, ARTIFACTS_DIR]:
        p.mkdir(parents=True, exist_ok=True)
