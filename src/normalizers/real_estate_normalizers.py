from __future__ import annotations
import pandas as pd
from pathlib import Path
from src.normalizers.common_timeseries import save_curated_df
from src.normalizers.common_timeseries import build_row
from datetime import datetime

# Helper to find latest raw file (simple date check)
def _find_latest_raw(base_dir: Path, dataset_name: str, filename: str) -> Path:
    # Pattern: data/raw/real_estate/{dataset_name}/{YYYY-MM-DD}/{filename}
    # We look for today's date first
    today_str = datetime.now().strftime("%Y-%m-%d")
    path = base_dir / f"data/raw/real_estate/{dataset_name}/{today_str}/{filename}"
    if path.exists():
        return path
    return None

def normalize_apt_price_index(base_dir: Path) -> Path:
    """
    Normalizes Real Estate Price Index (Mock/Hybrid) -> Standard CSV
    """
    dataset_id = "real_estate_price_index"
    entity = "KOR_RE_INDEX"
    
    raw_path = _find_latest_raw(base_dir, "housing_price_index", "price_index.csv")
    if not raw_path or not raw_path.exists():
        # print(f"[WARN] Raw file not found for {dataset_id}")
        return None

    df = pd.read_csv(raw_path)
    df = df[df['region'] == 'Nationwide'].copy()
    
    curated_rows = []
    for _, row in df.iterrows():
        ts_utc = f"{row['date']}T00:00:00Z"
        curated_rows.append(build_row(
            ts_utc=ts_utc,
            entity=entity,
            value=float(row['apt_price_index']),
            unit="INDEX",
            source=row.get('source', 'unknown'),
            dataset_id=dataset_id,
            metric_name="price_index",
            is_derived=False,
            derived_from=""
        ))

    target_path = base_dir / "data/curated/real_estate/price_index.csv"
    return save_curated_df(target_path, pd.DataFrame(curated_rows))

def normalize_apt_transaction_volume(base_dir: Path) -> Path:
    """
    Normalizes Transaction Volume -> Standard CSV
    """
    dataset_id = "real_estate_volume"
    entity = "KOR_RE_VOL"
    
    raw_path = _find_latest_raw(base_dir, "transaction_volume", "volume.csv")
    if not raw_path or not raw_path.exists():
        return None
        
    df = pd.read_csv(raw_path)
    df = df[df['region'] == 'Nationwide'].copy()
    
    curated_rows = []
    for _, row in df.iterrows():
        ts_utc = f"{row['date']}T00:00:00Z"
        curated_rows.append(build_row(
            ts_utc=ts_utc,
            entity=entity,
            value=float(row['transaction_count']),
            unit="COUNT",
            source=row.get('source', 'unknown'),
            dataset_id=dataset_id,
            metric_name="volume",
            is_derived=False,
            derived_from=""
        ))
    
    target_path = base_dir / "data/curated/real_estate/volume.csv"
    return save_curated_df(target_path, pd.DataFrame(curated_rows))

def normalize_unsold_inventory(base_dir: Path) -> Path:
    """
    Normalizes Unsold Inventory -> Standard CSV
    """
    dataset_id = "real_estate_unsold"
    entity = "KOR_RE_UNSOLD"
    
    raw_path = _find_latest_raw(base_dir, "unsold_inventory", "unsold.csv")
    if not raw_path or not raw_path.exists():
        return None

    df = pd.read_csv(raw_path)
    df = df[df['region'] == 'Nationwide'].copy()
    
    curated_rows = []
    for _, row in df.iterrows():
        ts_utc = f"{row['date']}T00:00:00Z"
        curated_rows.append(build_row(
            ts_utc=ts_utc,
            entity=entity,
            value=float(row['unsold_units']),
            unit="COUNT",
            source=row.get('source', 'unknown'),
            dataset_id=dataset_id,
            metric_name="unsold_inventory",
            is_derived=False,
            derived_from=""
        ))
    
    target_path = base_dir / "data/curated/real_estate/unsold.csv"
    return save_curated_df(target_path, pd.DataFrame(curated_rows))

