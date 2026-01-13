from pathlib import Path
from src.registry.loader import load_datasets, get_callables

def main():
    reg = Path("registry") / "datasets.yml"
    datasets = [d for d in load_datasets(reg) if d.enabled]
    for ds in datasets:
        # Pass the collector path string, not the whole config object
        fn = get_callables(ds.collector)
        fn(Path("."))

if __name__ == "__main__":
    main()
