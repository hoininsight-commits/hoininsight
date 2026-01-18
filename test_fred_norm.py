from pathlib import Path
from src.normalizers import fred_normalizers

print("Def:", fred_normalizers.normalize_fed_funds)

try:
    res = fred_normalizers.normalize_fed_funds(Path("."))
    print(f"Result: {res}")
    if res and res.exists():
        print("File exists!")
    else:
        print("File not found or None")
except Exception as e:
    print(f"Exception: {e}")
