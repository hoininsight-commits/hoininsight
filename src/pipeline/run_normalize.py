import sys
import traceback
from pathlib import Path
from src.registry.loader import load_datasets, get_callables

def main():
    reg = Path("registry") / "datasets.yml"
    datasets = [d for d in load_datasets(reg) if d.enabled]
    
    failure_count = 0
    
    for ds in datasets:
        try:
            fn = get_callables(ds.normalizer)
            fn(Path("."))
        except Exception as e:
            failure_count += 1
            print(f"error: normalizer failed for {ds.dataset_id}: {repr(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

    if failure_count > 0:
        print(f"normalize: finished with {failure_count} failures", file=sys.stderr)

if __name__ == "__main__":
    main()
