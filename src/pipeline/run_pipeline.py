import sys
import argparse
from src.engine import main as engine_main

def main():
    parser = argparse.ArgumentParser(description="Hoin Insight Pipeline Runner")
    parser.add_argument("--only-axis", type=str, help="Run only specific axis (CRYPTO, FX_RATES, US_MARKETS, BACKFILL)")
    parser.add_argument("--only-category", type=str, help="Run only specific category name directly")
    
    args = parser.parse_args()
    
    target_categories = None
    
    if args.only_axis:
        axis = args.only_axis.upper()
        if axis == "CRYPTO":
            target_categories = ["CRYPTO"]
        elif axis == "FX_RATES":
            target_categories = ["FX_RATES"]
        elif axis == "US_MARKETS":
            target_categories = ["GLOBAL_INDEX", "RATES_YIELD", "COMMODITIES", "PRECIOUS_METALS"]
        elif axis == "BACKFILL":
            target_categories = None # Run all
        else:
            print(f"Unknown axis: {axis}", file=sys.stderr)
            sys.exit(1)
            
        print(f"[RUN] axis={axis}", file=sys.stderr)

    elif args.only_category:
        target_categories = [args.only_category]
        print(f"[RUN] category={args.only_category}", file=sys.stderr)
        
    engine_main(target_categories)

if __name__ == "__main__":
    main()
