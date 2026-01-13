from pathlib import Path
from src.registry.loader import load_datasets, get_callables

def main():
    reg = Path("registry") / "datasets.yml"
    datasets = [d for d in load_datasets(reg) if d.enabled]
    for ds in datasets:
        fns = get_callables(ds)
        fns["collector"](Path("."))

if __name__ == "__main__":
    main()
