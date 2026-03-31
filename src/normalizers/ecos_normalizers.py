from __future__ import annotations

import pandas as pd
from pathlib import Path
from src.normalizers.common_timeseries import build_row, append_timeseries_csv

def _normalize_ecos_csv(raw_path: Path, curated_path: Path, entity: str, unit: str, metric_name: str, source: str = "ecos"):
    if not raw_path or not raw_path.exists():
        print(f"[WARN] Raw path not found: {raw_path}")
        return

    try:
        df = pd.read_csv(raw_path)
        # Expected columns: date, value
        if 'date' not in df.columns or 'value' not in df.columns:
            print(f"[WARN] Invalid ECOS CSV columns: {df.columns} in {raw_path}")
            return
            
        rows = []
        for _, row in df.iterrows():
            ts_str = str(row['date'])
            # ECOS collector saves as YYYY-MM-DD (from datetime conversion) or YYYY-MM-DD HH:MM:SS
            # We want ISO T separate
            if "T" not in ts_str:
                if len(ts_str) == 10: # YYYY-MM-DD
                    ts_str += "T00:00:00Z"
                elif len(ts_str) > 10: # YYYY-MM-DD HH:MM:SS
                     ts_str = ts_str.replace(" ", "T") + "Z"
            
            val = float(row['value'])
            
            norm_row = build_row(
                ts_utc=ts_str,
                entity=entity,
                value=val,
                unit=unit,
                source=source,
                dataset_id=f"ecos_{entity.lower()}", # approximate
                metric_name=metric_name,
                is_derived=False,
                derived_from=""
            )
            rows.append(norm_row)
            
        # Dedupe and Save
        # Reuse generic logic? We can just create DF and append
        # append_timeseries_csv handles single row, but we have many.
        # Let's do bulk save similar to market_normalizers
        
        df_norm = pd.DataFrame(rows)
        if curated_path.exists():
            old_df = pd.read_csv(curated_path)
            df_norm = pd.concat([old_df, df_norm], ignore_index=True)
            
        if "fingerprint" in df_norm.columns:
            df_norm = df_norm.drop_duplicates(subset=["fingerprint"], keep="last")
            
        curated_path.parent.mkdir(parents=True, exist_ok=True)
        df_norm.to_csv(curated_path, index=False)
        print(f"[OK] Normalized ECOS {entity} -> {curated_path}")

    except Exception as e:
        print(f"[ERR] Failed to normalize {raw_path}: {e}")

# --- Entry Points ---

def normalize_base_rate(base_dir: Path):
    # Find latest raw file provided by collector or just scan? 
    # Registry doesn't pass the raw path to normalizer directly. Normalizer must find it.
    # We use the same helper logic or just know the path.
    # ECOS path structure: data/raw/ecos/rates/YYYY/MM/DD/korea_base_rate.csv
    
    # We need to find the LATEST raw file to process.
    # Or process ALL raw files? Ideally just new ones.
    # For now, let's process the latest available one.
    
    from src.collectors.ecos_collector import _get_latest_ecos_path
    raw_path = _get_latest_ecos_path('rates', 'korea_base_rate')
    curated_path = base_dir / "data" / "curated" / "ecos" / "rates" / "korea_base_rate.csv"
    
    _normalize_ecos_csv(raw_path, curated_path, "KOR_BASE_RATE", "PCT", "interest_rate")

def normalize_cpi(base_dir: Path):
    from src.collectors.ecos_collector import _get_latest_ecos_path
    raw_path = _get_latest_ecos_path('inflation', 'korea_cpi')
    curated_path = base_dir / "data" / "curated" / "ecos" / "inflation" / "korea_cpi.csv"
    
    _normalize_ecos_csv(raw_path, curated_path, "KOR_CPI", "INDEX", "cpi_index")

def normalize_usdkrw(base_dir: Path):
    from src.collectors.ecos_collector import _get_latest_ecos_path
    raw_path = _get_latest_ecos_path('fx', 'korea_usdkrw')
    curated_path = base_dir / "data" / "curated" / "ecos" / "fx" / "usdkrw.csv"
    
    _normalize_ecos_csv(raw_path, curated_path, "KOR_USDKRW", "KRW", "exchange_rate")
