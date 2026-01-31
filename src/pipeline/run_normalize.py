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
        print(f"normalize: running for categories={target_categories} (count={len(datasets)})", file=sys.stderr)
    else:
        datasets = [d for d in all_datasets if d.enabled]
    
    # Load existing status
    status_dir = Path("data/dashboard")
    status_file = status_dir / "collection_status.json"
    collection_status = {}
    
    if status_file.exists():
        try:
            with open(status_file, "r", encoding="utf-8") as f:
                collection_status = json.load(f)
        except Exception:
            pass

    failure_count = 0
    
    for ds in datasets:
        dataset_id = ds.dataset_id
        
        try:
            fn = get_callables(ds.normalizer)
            fn(Path("."))
            
            # If normalization succeeds, mark as OK (unless it was explicitly SKIP/WARMUP)
            current_status = collection_status.get(dataset_id, {}).get("status", "FAIL")
            
            if current_status not in ["SKIP", "WARMUP"]:
                collection_status[dataset_id] = {
                    "status": "OK",
                    "reason": "Normalized successfully",
                    "timestamp": datetime.now().isoformat() + "Z"
                }
            else:
                 # If it was SKIP/WARMUP, keep it but update timestamp
                 collection_status[dataset_id]["timestamp"] = datetime.now().isoformat() + "Z"
            
        except Exception as e:
            failure_count += 1
            print(f"error: normalizer failed for {ds.dataset_id}: {repr(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            
            # Update status to FAIL if normalization fails
            collection_status[dataset_id] = {
                "status": "FAIL",
                "reason": f"Normalization Error: {str(e)[:100]}",
                "timestamp": datetime.now().isoformat() + "Z"
            }

    # Save updated status
    status_dir.mkdir(parents=True, exist_ok=True)
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(collection_status, f, indent=2)

    if failure_count > 0:
        print(f"normalize: finished with {failure_count} failures", file=sys.stderr)

if __name__ == "__main__":
    main()
