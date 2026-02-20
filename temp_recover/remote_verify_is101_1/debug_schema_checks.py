import sys
from pathlib import Path
from src.validation.schema_check import run_schema_checks

def verify_schemas():
    print("Running schema checks...")
    try:
        res = run_schema_checks(Path("."), None)
        if res.ok:
            print("Schema Checks PASS")
            sys.exit(0)
        else:
            print("Schema Checks FAIL")
            for line in res.lines:
                print(line)
            sys.exit(1)
    except Exception as e:
        print(f"Exception during schema checks: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    verify_schemas()
