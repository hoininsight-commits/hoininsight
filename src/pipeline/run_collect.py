import sys
import json
import traceback
from datetime import datetime
from pathlib import Path
from src.registry.loader import load_datasets, get_callables

def main():
    reg = Path("registry") / "datasets.yml"
    datasets = [d for d in load_datasets(reg) if d.enabled]
    
    # Track collection status for each dataset
    collection_status = {}
    failure_count = 0
    
    for ds in datasets:
        dataset_id = ds.dataset_id
        status = "FAIL"
        reason = "Unknown error"
        
        try:
            fn = get_callables(ds.collector)
            fn(Path("."))
            # If no exception, assume success
            status = "OK"
            reason = "Collected successfully"
        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            
            # Detect SKIP vs FAIL based on error message
            if "mock" in error_msg.lower() or "skip" in error_msg.lower():
                status = "SKIP"
                reason = f"Skipped: {error_msg[:100]}"
            else:
                status = "FAIL"
                reason = f"Error: {error_msg[:100]}"
            
            print(f"error: collector failed for {dataset_id}: {repr(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        
        # Record status
        collection_status[dataset_id] = {
            "status": status,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    # Save collection status to JSON
    status_dir = Path("data/dashboard")
    status_dir.mkdir(parents=True, exist_ok=True)
    status_file = status_dir / "collection_status.json"
    
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(collection_status, f, indent=2)
    
    print(f"Collection status saved to {status_file}", file=sys.stderr)

    if failure_count > 0:
        print(f"collect: finished with {failure_count} failures (check logs)", file=sys.stderr)

if __name__ == "__main__":
    main()
