from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# --- Primary SSOT Authority Paths ---
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CURATED_DIR = DATA_DIR / "curated"
FEATURES_DIR = DATA_DIR / "features"
TOPICS_DIR = DATA_DIR / "topics"
DECISION_DIR = DATA_DIR / "decision"
OPS_DIR = DATA_DIR / "ops"
REPORTS_DIR = DATA_DIR / "reports"

# --- Published UI Authority Paths ---
DOCS_DIR = ROOT / "docs"
DOCS_UI_DIR = DOCS_DIR / "ui"
DOCS_DATA_DIR = DOCS_DIR / "data"

# --- Legacy Compatibility Paths (Deprecated for new logic) ---
DATA_OUTPUTS_DIR = ROOT / "data_outputs"
LEGACY_OPS_DIR = DATA_OUTPUTS_DIR / "ops"

def ensure_dirs():
    """Ensure all primary authority directories exist."""
    dirs = [
        RAW_DIR, CURATED_DIR, FEATURES_DIR, TOPICS_DIR, 
        DECISION_DIR, OPS_DIR, REPORTS_DIR,
        DOCS_DATA_DIR, LEGACY_OPS_DIR
    ]
    for p in dirs:
        p.mkdir(parents=True, exist_ok=True)
