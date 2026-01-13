from pathlib import Path
from src.registry.loader import load_datasets
from src.anomaly_detectors.roc_1d import detect_roc_1d

def main():
    reg = Path("registry") / "datasets.yml"
    datasets = [d for d in load_datasets(reg) if d.enabled]

    for ds in datasets:
        # curated 경로는 현재 구현된 2개 데이터셋만 매핑(추후 registry로 일반화)
        if ds.report_key == "BTCUSD":
            curated = Path(".") / "data" / "curated" / "crypto" / "btc_usd.csv"
        elif ds.report_key == "USDKRW":
            curated = Path(".") / "data" / "curated" / "fx" / "usdkrw.csv"
        else:
            raise RuntimeError(f"unknown report_key mapping: {ds.report_key}")

        detect_roc_1d(Path("."), dataset_id=ds.dataset_id, curated_csv=curated, entity=ds.entity, threshold_pct=3.0)

if __name__ == "__main__":
    main()
