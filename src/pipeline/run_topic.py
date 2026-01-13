from pathlib import Path
from datetime import datetime
from src.registry.loader import load_datasets, get_callables

def main():
    y = datetime.utcnow().strftime("%Y")
    m = datetime.utcnow().strftime("%m")
    d = datetime.utcnow().strftime("%d")
    anomalies_path = Path(".") / "data" / "features" / "anomalies" / y / m / d / "anomalies.json"

    reg = Path("registry") / "datasets.yml"
    datasets = [ds for ds in load_datasets(reg) if ds.enabled]
    for ds in datasets:
        fns = get_callables(ds)
        fns["topic"](Path("."), anomalies_path)

if __name__ == "__main__":
    main()
