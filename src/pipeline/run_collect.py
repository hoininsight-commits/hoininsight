from pathlib import Path
from src.collectors.coingecko_btc import write_raw_quote

def main():
    write_raw_quote(Path("."))

if __name__ == "__main__":
    main()
