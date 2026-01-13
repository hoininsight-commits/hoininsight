from pathlib import Path
from src.registry.loader import load_datasets
from src.anomaly_detectors.roc_1d import detect_roc_1d

def main():
    reg = Path("registry") / "datasets.yml"
    datasets = [d for d in load_datasets(reg) if d.enabled]

    for ds in datasets:
        # Use dynamic path from registry instead of hardcoded mapping
        curated = Path(".") / ds.curated_path
        
        # Check if file exists before processing to avoid crashes on missing data
        if not curated.exists():
            continue

        detect_roc_1d(Path("."), dataset_id=ds.dataset_id, curated_csv=curated, entity=ds.entity, threshold_pct=3.0)

if __name__ == "__main__":
    main()
