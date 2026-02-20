import json
from pathlib import Path
from typing import Dict, Any


def calculate_regime_confidence(status_path: Path) -> Dict[str, Any]:
    """
    Calculates Regime Confidence based on Core Dataset collection status.
    
    Rules:
      - HIGH: All 3 Core Datasets are OK
      - MEDIUM: 2 or more OK (others SKIP/WARMUP)
      - LOW: 1 or fewer OK OR any FAIL status
    """
    # Core Datasets to check
    core_datasets = {
        "rates_us10y_yield_ustreasury": "US10Y",
        "index_spx_sp500_stooq": "SPX",
        "crypto_btc_usd_spot_coingecko": "BTC"
    }
    
    # Expected paths for fallback check (Hardcoded for reliability)
    fallback_paths = {
        "rates_us10y_yield_ustreasury": "data/curated/rates/us10y.csv",
        "index_spx_sp500_stooq": "data/curated/indices/spx.csv",
        "crypto_btc_usd_spot_coingecko": "data/curated/crypto/btc_usd.csv"
    }
    
    # Determine base directory for fallback paths relative to status_path
    # Assuming status_path is like 'data/status/regime_status.json'
    # We need to go up to 'data/' then to 'data/curated/'
    base_dir = status_path.parent.parent # This should point to the 'data' directory
    
    confidence = "LOW"
    breakdown = {}
    
    if not status_path.exists():
        return {
            "regime_confidence": "LOW",
            "reason": "Status file missing",
            "core_breakdown": {}
        }

    try:
        status_data = json.loads(status_path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "regime_confidence": "LOW",
            "reason": "Status file corrupt",
            "core_breakdown": {}
        }
        
    ok_count = 0
    fail_exists = False
    
    import datetime
    
    for ds_id, label in core_datasets.items():
        # Default to FAIL if missing from status
        s_info = status_data.get(ds_id, {"status": "FAIL"})
        st = s_info.get("status", "FAIL")
        
        # [Emergency Reliability Fix]
        # If JSON says FAIL, check if actual curated file exists and is valid
        if st != "OK":
            try:
                rel_path = fallback_paths.get(ds_id)
                if rel_path:
                    # Resolve path: status_path is data/dashboard/collection_status.json
                    # project root is 2 levels up from data/dashboard -> data -> root?
                    # No, status_path is absolute usually?
                    # Let's rely on status_path.parent.parent.parent (Project Root) 
                    # status_path: .../HoinInsight/data/dashboard/collection_status.json
                    # parent: .../HoinInsight/data/dashboard
                    # parent.parent: .../HoinInsight/data
                    # parent.parent.parent: .../HoinInsight (Root)
                    proj_root = status_path.parent.parent.parent
                    fpath = proj_root / rel_path
                    
                    if fpath.exists() and fpath.stat().st_size > 0:
                        # Check modification time (within 24h)
                        mtime = fpath.stat().st_mtime
                        if (datetime.datetime.now().timestamp() - mtime) < 86400:
                            st = "OK"
            except Exception:
                pass
        
        breakdown[label] = st
        
        if st == "OK":
            ok_count += 1
        elif st == "FAIL":
            fail_exists = True
            
    # Evaluation Logic
    if fail_exists:
        confidence = "LOW"
    elif ok_count == 3:
        confidence = "HIGH"
    elif ok_count >= 2:
        confidence = "MEDIUM"
    else:
        confidence = "LOW" # 0 or 1 OK
        
    return {
        "regime_confidence": confidence,
        "core_breakdown": breakdown
    }
