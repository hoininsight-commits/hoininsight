from pathlib import Path
import glob

base_dir = Path(".")
category = "rates"
name = "fed_funds_rate"

raw_root = base_dir / "data" / "raw" / "fred" / category
print(f"Raw root: {raw_root} (Exists: {raw_root.exists()})")

pattern = str(raw_root / "**" / f"{name}.csv")
print(f"Pattern: {pattern}")

files = glob.glob(pattern, recursive=True)
print(f"Files found: {len(files)}")
for f in files:
    print(f" - {f}")

# Try absolute path
abs_root = raw_root.resolve()
print(f"Abs root: {abs_root}")
pattern_abs = str(abs_root / "**" / f"{name}.csv")
print(f"Pattern Abs: {pattern_abs}")
files_abs = glob.glob(pattern_abs, recursive=True)
print(f"Files found (abs): {len(files_abs)}")
