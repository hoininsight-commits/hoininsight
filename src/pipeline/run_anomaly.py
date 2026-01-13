from pathlib import Path
from src.registry.loader import load_datasets, get_callables

def main():
    reg = Path("registry") / "datasets.yml"
    datasets = [d for d in load_datasets(reg) if d.enabled]
    for ds in datasets:
        fns = get_callables(ds)
        fns["anomaly"](Path("."), threshold_pct=3.0)

if __name__ == "__main__":
    main()
