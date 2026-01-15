import sys
import json
import traceback
from datetime import datetime
from pathlib import Path
from src.registry.loader import load_datasets, get_callables

def main(target_categories: list[str] = None):
    reg = Path("registry") / "datasets.yml"
    all_datasets = load_datasets(reg)
    
    if target_categories:
        datasets = [d for d in all_datasets if d.enabled and d.category in target_categories]
        print(f"collect: running for categories={target_categories} (count={len(datasets)})", file=sys.stderr)
    else:
        datasets = [d for d in all_datasets if d.enabled]
    
    # Track collection status for each dataset
    collection_status = {}
    failure_count = 0
    
    for ds in datasets:
        dataset_id = ds.dataset_id
        status = "FAIL"
        reason = "Unknown error"
        
        try:
            fn = get_callables(ds.collector)
            out_path = fn(Path("."))
            
            # If no exception, assume success initially
            status = "OK"
            reason = "Collected successfully"

            # Check for mock data in the output file
            if isinstance(out_path, Path) and out_path.exists():
                try:
                    content = json.loads(out_path.read_text(encoding="utf-8"))
                    src = content.get("source", "").lower()
                    if "mock" in src:
                        status = "SKIP"
                        reason = f"Mock data used ({src})"
                except Exception:
                    # Not a JSON file or read error, ignore check
                    pass
            elif str(out_path).endswith(".json") or str(out_path).endswith(".jsonl"):
                # Path object might be returned but we want robustness; 
                # but if fn returned None, we can't check.
                pass
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
