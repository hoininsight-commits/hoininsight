
import pandas as pd
from pathlib import Path
from datetime import datetime
import glob
import os
from src.normalizers.common_timeseries import build_row, append_timeseries_csv

def _find_latest_fred_file(base_dir: Path, category: str, name: str) -> Path:
    """Find the latest raw file for a given FRED category and name."""
    # Pattern: data/raw/fred/{category}/*/*/*/{name}.csv
    # But checking all dates is expensive. Let's look for today's date first, then fallback?
    # Or just use glob to find all and pick last.
    
    raw_root = base_dir / "data" / "raw" / "fred" / category
    if not raw_root.exists():
        return None
        
    # Search recursively for the file
    pattern = str(raw_root / "**" / f"{name}.csv") # raw_root/YYYY/MM/DD/name.csv
    files = glob.glob(pattern, recursive=True)
    
    if not files:
        return None
        
    # Sort by path (which contains date structure YYYY/MM/DD) so last is latest
    files.sort()
    return Path(files[-1])

def _normalize_fred_generic(
    base_dir: Path,
    dataset_id: str,
    raw_category: str,
    raw_name: str,
    entity: str,
    unit: str,
    metric_name: str,
    curated_subpath: str,
    source: str = "fred"
):
    """Generic normalizer for FRED data"""
    try:
        raw_path = _find_latest_fred_file(base_dir, raw_category, raw_name)
        if not raw_path:
            print(f"[WARN] No raw file found for {dataset_id} ({raw_category}/{raw_name}) in {base_dir}")
            return None

        # Read raw CSV (date, value)
        df = pd.read_csv(raw_path)
        
        normalized_rows = []
        for _, row in df.iterrows():
            date_str = str(row['date']).split()[0]
            try:
                # FRED dates are usually YYYY-MM-DD
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                # System expects ISO string for ts_utc?
                ts_utc = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                
                val = float(row['value'])
                if pd.isna(val):
                    continue

                norm_row = build_row(
                    ts_utc=ts_utc,
                    entity=entity,
                    value=val,
                    unit=unit,
                    source=source,
                    dataset_id=dataset_id,
                    metric_name=metric_name,
                    is_derived=False,
                    derived_from=""
                )
                normalized_rows.append(norm_row)
            except Exception as e:
                print(f"[ERR] Row fail: {e}")
                continue
        
        if not normalized_rows:
            return None

        # Bulk Save Logic
        curated_path = base_dir / curated_subpath
        curated_path.parent.mkdir(parents=True, exist_ok=True)
        
        df_new = pd.DataFrame(normalized_rows)
        
        if curated_path.exists():
            try:
                df_old = pd.read_csv(curated_path)
                df_final = pd.concat([df_old, df_new], ignore_index=True)
            except Exception:
                df_final = df_new
        else:
            df_final = df_new

        # Deduplicate
        if "fingerprint" in df_final.columns:
            df_final = df_final.drop_duplicates(subset=["fingerprint"], keep="last")
        
        df_final.to_csv(curated_path, index=False)
        print(f"[OK] Normalized FRED {entity} -> {curated_path}")
        return curated_path

    except Exception as e:
        print(f"[ERR] FRED Normalize failed {dataset_id}: {e}")
        return None

def normalize_fed_funds(base_dir: Path):
    return _normalize_fred_generic(
        base_dir, 
        "rates_fed_funds_fred", 
        "rates", "fed_funds_rate", 
        "FEDFUNDS", "PCT", "interest_rate", 
        "data/curated/rates/fed_funds.csv"
    )

def normalize_cpi(base_dir: Path):
    return _normalize_fred_generic(
        base_dir,
        "inflation_cpi_fred",
        "inflation", "cpi",
        "CPI", "INDEX", "cpi",
        "data/curated/inflation/cpi_usa.csv"
    )

def normalize_pce(base_dir: Path):
    return _normalize_fred_generic(
        base_dir,
        "inflation_pce_fred",
        "inflation", "pce",
        "PCE", "USD_BN", "pce",
        "data/curated/inflation/pce_usa.csv"
    )

def normalize_m2(base_dir: Path):
    return _normalize_fred_generic(
        base_dir,
        "liquidity_m2_fred",
        "money_supply", "m2",
        "M2", "USD_BN", "money_supply",
        "data/curated/liquidity/m2_usa.csv"
    )

def normalize_unrate(base_dir: Path):
    return _normalize_fred_generic(
        base_dir,
        "employment_unrate_fred",
        "employment", "unemployment_rate",
        "UNRATE", "PCT", "unemployment_rate",
        "data/curated/employment/unrate_usa.csv"
    )

def normalize_hy_spread(base_dir: Path):
    return _normalize_fred_generic(
        base_dir,
        "credit_hy_spread_fred",
        "credit", "hy_spread",
        "HY_SPREAD", "PCT", "spread",
        "data/curated/credit/hy_spread_usa.csv"
    )

def normalize_financial_stress(base_dir: Path):
    return _normalize_fred_generic(
        base_dir,
        "risk_financial_stress_fred",
        "credit", "financial_stress",
        "FIN_STRESS", "INDEX", "stress_index",
        "data/curated/risk/financial_stress_usa.csv"
    )

def normalize_vix(base_dir: Path):
    return _normalize_fred_generic(
        base_dir,
        "risk_vix_fred",
        "market", "vix",
        "VIX", "INDEX", "close",
        "data/curated/risk/vix.csv"
    )

def normalize_sp500(base_dir: Path):
    return _normalize_fred_generic(
        base_dir,
        "index_spx_fred",
        "market", "sp500",
        "SPX", "INDEX", "close",
        "data/curated/indices/spx.csv"
    )

def normalize_nasdaq(base_dir: Path):
    return _normalize_fred_generic(
        base_dir,
        "index_nasdaq_fred",
        "market", "nasdaq100",
        "NDX", "INDEX", "close",
        "data/curated/indices/nasdaq.csv"
    )

def normalize_wti(base_dir: Path):
    return _normalize_fred_generic(
        base_dir,
        "comm_wti_fred",
        "market", "wti",
        "WTI", "USD", "close",
        "data/curated/commodities/wti.csv"
    )

def normalize_gold(base_dir: Path):
    return _normalize_fred_generic(
        base_dir,
        "metal_gold_fred",
        "market", "gold",
        "XAUUSD", "USD", "close",
        "data/curated/metals/gold_usd.csv"
    )

def normalize_silver(base_dir: Path):
    return _normalize_fred_generic(
        base_dir,
        "metal_silver_fred",
        "market", "silver",
        "XAGUSD", "USD", "close",
        "data/curated/metals/silver_usd.csv"
    )

def normalize_us10y(base_dir: Path):
    return _normalize_fred_generic(
        base_dir,
        "rates_us10y_fred",
        "rates", "us_10y_yield",
        "US10Y", "PCT", "yield",
        "data/curated/rates/us10y.csv"
    )

def normalize_us2y(base_dir: Path):
    return _normalize_fred_generic(
        base_dir,
        "rates_us02y_fred",
        "rates", "us_2y_yield",
        "US02Y", "PCT", "yield",
        "data/curated/rates/us02y.csv"
    )
