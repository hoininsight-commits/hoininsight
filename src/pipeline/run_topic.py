from pathlib import Path
from datetime import datetime
from src.registry.loader import load_datasets
from src.topic_selectors.simple_topic import select_topics

def main():
    y = datetime.utcnow().strftime("%Y")
    m = datetime.utcnow().strftime("%m")
    d = datetime.utcnow().strftime("%d")

    reg = Path("registry") / "datasets.yml"
    datasets = [ds for ds in load_datasets(reg) if ds.enabled]

    for ds in datasets:
        anomalies_path = Path(".") / "data" / "features" / "anomalies" / y / m / d / f"{ds.dataset_id}.json"
        select_topics(Path("."), ds.dataset_id, anomalies_path)

if __name__ == "__main__":
    main()
