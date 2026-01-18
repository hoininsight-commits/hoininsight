import sys
import traceback
import importlib
from pathlib import Path
from src.registry.loader import load_datasets

def _get_func_by_name(func_path_str: str):
    """
    Parses 'module.path:func_name' and returns the function object.
    """
    try:
        mod_curr, func_name = func_path_str.split(":")
        module = importlib.import_module(mod_curr)
        return getattr(module, func_name)
    except Exception as e:
        raise ImportError(f"Could not load function '{func_path_str}': {e}")

def main():
    reg = Path("registry") / "datasets.yml"
    datasets = [d for d in load_datasets(reg) if d.enabled]

    failure_count = 0

    for ds in datasets:
        try:
            curated = Path(".") / ds.curated_path
            
            # Check if file exists before processing
            if not curated.exists():
                # Expected if collection failed
                continue

            # Load Dynamic Anomaly Detector
            detector_func_path = getattr(ds, 'anomaly', None)
            
            if not detector_func_path:
                # Fallback to old default if not specified (though strict schema requires it)
                print(f"[WARN] No anomaly function specified for {ds.dataset_id}, skipping.")
                continue
                
            detector = _get_func_by_name(detector_func_path)
            
            # Detect
            # detectors usually signature: (base_dir, dataset_id, curated_csv, entity)
            detector(
                base_dir=Path("."), 
                dataset_id=ds.dataset_id, 
                curated_csv=curated, 
                entity=ds.entity
            )
            
        except Exception as e:
            failure_count += 1
            print(f"error: anomaly detection failed for {ds.dataset_id}: {repr(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

    if failure_count > 0:
        print(f"anomaly: finished with {failure_count} failures", file=sys.stderr)

if __name__ == "__main__":
    main()
