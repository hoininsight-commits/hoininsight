import sys
import traceback
from pathlib import Path
from src.registry.loader import load_datasets
from src.anomaly_detectors.roc_1d import detect_roc_1d

def main():
    reg = Path("registry") / "datasets.yml"
    datasets = [d for d in load_datasets(reg) if d.enabled]

    failure_count = 0

    for ds in datasets:
        try:
            curated = Path(".") / ds.curated_path
            
            # Check if file exists before processing
            if not curated.exists():
                # If curated missing, we can't run anomaly. 
                # This is expected if collection failed.
                continue

            detect_roc_1d(Path("."), dataset_id=ds.dataset_id, curated_csv=curated, entity=ds.entity, threshold_pct=3.0)
        except Exception as e:
            failure_count += 1
            print(f"error: anomaly detection failed for {ds.dataset_id}: {repr(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

    if failure_count > 0:
        print(f"anomaly: finished with {failure_count} failures", file=sys.stderr)

if __name__ == "__main__":
    main()
