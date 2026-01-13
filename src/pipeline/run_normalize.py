from pathlib import Path
from src.normalizers.btc_curated import write_curated_csv

def main():
    write_curated_csv(Path("."))

if __name__ == "__main__":
    main()
