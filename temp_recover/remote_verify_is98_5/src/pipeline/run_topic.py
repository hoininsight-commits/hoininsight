import sys
import traceback
from pathlib import Path
from datetime import datetime
from src.registry.loader import load_datasets
from src.topic_selectors.simple_topic import select_topics

def main():
    y = datetime.now().strftime("%Y")
    m = datetime.now().strftime("%m")
    d = datetime.now().strftime("%d")

    reg = Path("registry") / "datasets.yml"
    datasets = [ds for ds in load_datasets(reg) if ds.enabled]

    failure_count = 0

    for ds in datasets:
        try:
            anomalies_path = Path(".") / "data" / "features" / "anomalies" / y / m / d / f"{ds.dataset_id}.json"
            
            # Robustness: Skip finding topics if anomaly detection failed (file missing)
            if not anomalies_path.exists():
                continue

            select_topics(Path("."), ds.dataset_id, anomalies_path)
            
        except Exception as e:
            failure_count += 1
            print(f"error: topic selection failed for {ds.dataset_id}: {repr(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

    if failure_count > 0:
        print(f"topic: finished with {failure_count} failures", file=sys.stderr)

if __name__ == "__main__":
    main()
