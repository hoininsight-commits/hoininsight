from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# --- Primary SSOT Authority Paths (Single Source of Truth) ---
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CURATED_DIR = DATA_DIR / "curated"
FEATURES_DIR = DATA_DIR / "features"
TOPICS_DIR = DATA_DIR / "topics"
DECISION_DIR = DATA_DIR / "decision"  # Authority for final decision cards
OPS_DIR = DATA_DIR / "ops"           # Authority for operational state (regime, timing, etc.)
REPORTS_DIR = DATA_DIR / "reports"

# --- Published UI Assets (Live environment for Dashboard) ---
DOCS_DIR = ROOT / "docs"
DOCS_UI_DIR = DOCS_DIR / "ui"
DOCS_DATA_DIR = DOCS_DIR / "data"    # Live data loaded by dashboard

# --- Legacy Compatibility Paths (DEPRECATED: Avoid using in new logic) ---
# data_outputs is kept for backward compatibility with 2025 scripts.
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
