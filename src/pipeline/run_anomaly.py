from pathlib import Path
from src.anomaly_detectors.roc_1d import detect_roc_1d

def main():
    detect_roc_1d(Path("."), threshold_pct=3.0)

if __name__ == "__main__":
    main()
