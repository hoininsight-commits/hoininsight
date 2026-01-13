import sys
import traceback
from pathlib import Path
from src.registry.loader import load_datasets, get_callables

def main():
    reg = Path("registry") / "datasets.yml"
    datasets = [d for d in load_datasets(reg) if d.enabled]
    
    # We want to run all collectors. If one fails, log it and continue.
    # The output_check phase will later detect missing files and handle soft/hard fail logic.
    failure_count = 0
    
    for ds in datasets:
        try:
            fn = get_callables(ds.collector)
            fn(Path("."))
        except Exception as e:
            failure_count += 1
            print(f"error: collector failed for {ds.dataset_id}: {repr(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            # We CONTINUE here so other datasets can still be collected.

    if failure_count > 0:
        print(f"collect: finished with {failure_count} failures (check logs)", file=sys.stderr)

if __name__ == "__main__":
    main()
