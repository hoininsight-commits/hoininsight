from __future__ import annotations
import pandas as pd
from pathlib import Path
from datetime import datetime
from src.normalizers.common_timeseries import save_curated_df, build_row

def _find_latest_raw(base_dir: Path, dataset_name: str, filename: str) -> Path:
    today_str = datetime.now().strftime("%Y-%m-%d")
    path = base_dir / f"data/raw/structural_capital/{dataset_name}/{today_str}/{filename}"
    if path.exists():
        return path
    return None

def normalize_dart_filing_count(base_dir: Path) -> Path:
    """
    Normalizes DART Filings (Event List) -> Daily Event Count Time Series
    Note: datasets.yml points to this function for BOTH 'cb_bw' and 'disposal'.
    But wait, I need to know WHICH one I'm normalizer.
    
    In datasets.yml, I assigned:
    - struct_dart_cb_bw -> normalize_dart_filing_count
    - struct_dart_disposal -> normalize_dart_filing_count
    
    This ambiguity is a problem if I don't know the dataset_id.
    Standard solution: Create two separate wrapper functions.
    """
    # This function shouldn't be called directly if we need distinction.
    # I will rename this to internal and expose two wrappers below.
    pass

def normalize_dart_cb_bw(base_dir: Path) -> Path:
    return _normalize_dart_filing_generic(base_dir, "cb_bw_filings", "cb_bw.csv", "struct_dart_cb_bw", "DART_CB_BW")

def normalize_dart_disposal(base_dir: Path) -> Path:
    return _normalize_dart_filing_generic(base_dir, "disposal_filings", "disposal.csv", "struct_dart_disposal", "DART_DISPOSAL")

def _normalize_dart_filing_generic(base_dir: Path, folder: str, file: str, ds_id: str, entity: str) -> Path:
    raw_path = _find_latest_raw(base_dir, folder, file)
    if not raw_path or not raw_path.exists():
        return None

    df = pd.read_csv(raw_path)
    daily_counts = df.groupby('date').size().reset_index(name='value')
    
    curated_rows = []
    for _, row in daily_counts.iterrows():
        ts_utc = f"{row['date']}T18:00:00Z"
        curated_rows.append(build_row(
            ts_utc=ts_utc,
            entity=entity,
            value=float(row['value']),
            unit="COUNT",
            source="dart",
            dataset_id=ds_id,
            metric_name="filing_count",
            is_derived=False,
            derived_from=""
        ))
    
    if "cb_bw" in ds_id:
        target_path = base_dir / "data/curated/structural/cb_bw.csv"
    else:
        target_path = base_dir / "data/curated/structural/disposal.csv"
        
    return save_curated_df(target_path, pd.DataFrame(curated_rows))

def normalize_krx_foreigner_flow(base_dir: Path) -> Path:
    """
    Normalizes KRX Foreigner Net Buy (Top 10) -> Aggregated Volume Time Series
    """
    dataset_id = "struct_krx_foreigner_flow"
    entity = "KRX_FOREIG_TOP10"
    
    raw_path = _find_latest_raw(base_dir, "foreigner_capital_flow", "top10_flow.csv")
    if not raw_path or not raw_path.exists():
        return None

    df = pd.read_csv(raw_path)
    daily_sum = df.groupby('date')['net_buy_amount'].sum().reset_index(name='value')
    
    curated_rows = []
    for _, row in daily_sum.iterrows():
        ts_utc = f"{row['date']}T18:00:00Z"
        curated_rows.append(build_row(
            ts_utc=ts_utc,
            entity=entity,
            value=float(row['value']),
            unit="KRW",
            source="pykrx",
            dataset_id=dataset_id,
            metric_name="net_buy_volume",
            is_derived=False,
            derived_from=""
        ))
    
    target_path = base_dir / "data/curated/structural/foreigner_flow.csv"
    return save_curated_df(target_path, pd.DataFrame(curated_rows))
