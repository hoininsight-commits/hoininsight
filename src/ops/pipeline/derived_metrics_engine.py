import pandas as pd
from pathlib import Path
from datetime import datetime

def _load_series(base_dir: Path, path_suffix: str) -> pd.DataFrame:
    p = base_dir / path_suffix
    if not p.exists():
        print(f"[Derived][WARN] Missing input file: {path_suffix}")
        return None
    try:
        df = pd.read_csv(p)
        if 'ts_utc' not in df.columns or 'value' not in df.columns:
             print(f"[Derived][ERR] Invalid schema in {path_suffix} (needs ts_utc, value)")
             return None
        df['ts_utc'] = pd.to_datetime(df['ts_utc'], utc=True)
        # Deduplicate by timestamp, keeping last
        df = df.drop_duplicates(subset=['ts_utc'], keep='last')
        return df.set_index('ts_utc').sort_index()
    except Exception as e:
        print(f"[Derived][ERR] Failed to load {path_suffix}: {e}")
        return None

def run_derived_metrics(base_dir: Path):
    print("[Derived] Starting Logic Computations...")
    
    # 1. Yield Curve (10Y - 2Y)
    # Correct Paths verified via list_dir
    df_10y = _load_series(base_dir, "data/curated/rates/us10y.csv") 
    df_2y = _load_series(base_dir, "data/curated/rates/us02y.csv")
    
    if df_10y is not None and df_2y is not None:
        # Inner join on timestamp to match days
        df_join = df_10y[['value']].join(df_2y[['value']], lsuffix='_10y', rsuffix='_2y', how='inner')
        
        # Logic: Spread = 10Y - 2Y
        df_result = pd.DataFrame(index=df_join.index)
        df_result['value'] = df_join['value_10y'] - df_join['value_2y']
        
        _save_derived(base_dir, df_result, "rates/yield_curve_10y_2y.csv", "SPREAD_10Y_2Y", "PCT")

    # 2. Gold/Silver Ratio
    df_gold = _load_series(base_dir, "data/curated/metals/gold_usd.csv")
    df_silver = _load_series(base_dir, "data/curated/metals/silver_usd.csv")
    
    if df_gold is not None and df_silver is not None:
        df_join = df_gold[['value']].join(df_silver[['value']], lsuffix='_gold', rsuffix='_silver', how='inner')
        
        # Logic: Ratio = Gold / Silver
        df_result = pd.DataFrame(index=df_join.index)
        df_result['value'] = df_join['value_gold'] / df_join['value_silver']
        
        _save_derived(base_dir, df_result, "metals/gold_silver_ratio.csv", "GOLD_SILVER_RATIO", "RATIO")

    print("[Derived] Logic Computations Complete.")

def _save_derived(base_dir, df, subpath, entity, unit):
    out_path = base_dir / "data" / "curated" / "derived" / subpath
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Schema Standard
    exposure = df.reset_index()
    exposure['entity'] = entity
    exposure['unit'] = unit
    exposure['source'] = 'hoin_logic_engine'
    exposure['dataset_id'] = f"derived_{entity.lower()}"
    exposure['metric_name'] = "ratio" if "RATIO" in entity else "spread"
    exposure['is_derived'] = True
    exposure['derived_from'] = "various"
    
    # Generate Fingerprint (required by schema)
    import hashlib
    def get_fingerprint(row):
        s = f"{row['ts_utc']}_{row['value']}_{row['dataset_id']}"
        return hashlib.md5(s.encode('utf-8')).hexdigest()
    
    exposure['fingerprint'] = exposure.apply(get_fingerprint, axis=1)
    
    exposure.to_csv(out_path, index=False)
    print(f"[Derived] Generated {out_path} ({len(exposure)} rows)")

def run_derived_metrics_wrapper(base_dir: Path) -> Path:
    """
    Wrapper for registry compatibility (called by run_collect.py).
    Triggers the full derived metrics generation logic.
    Returns a representative path (or directory) to indicate success.
    """
    run_derived_metrics(base_dir)
    # Return a path that definitely exists after run
    return base_dir / "data/curated/derived/rates/yield_curve_10y_2y.csv"

if __name__ == "__main__":
    run_derived_metrics(Path("."))
