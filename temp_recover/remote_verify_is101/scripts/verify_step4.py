import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.tickers.ticker_linker_engine import TickerLinkerEngine
from src.tickers.company_map_registry import Step3BottleneckSignal

def main():
    base_dir = Path(".")
    out_dir = base_dir / "data" / "decision" / "locked_ticker_cards"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    engine = TickerLinkerEngine()
    
    scenarios = [
        (
            Step3BottleneckSignal(
                trigger="IMO EEXI/CII Enforced",
                forced_capex="Ammonia/Dual-Fuel Engines",
                bottleneck_slot="GREEN_SHIP_CORE_SYSTEM"
            ),
            "mock_policy.json"
        ),
        (
            Step3BottleneckSignal(
                trigger="US Transformer Shortage",
                forced_capex="UHV Transformers",
                bottleneck_slot="HV_TRANSFORMER_LEADTIME"
            ),
            "mock_supply_chain.json"
        ),
        (
            Step3BottleneckSignal(
                trigger="NVIDIA Blackwell Launch",
                forced_capex="HBM3E",
                bottleneck_slot="HBM_STACKED_MEMORY"
            ),
            "mock_tech_phase.json"
        )
    ]
    
    print("=== Step 4 Verification Run ===")
    
    for signal, filename in scenarios:
        print(f"\nProcessing: {signal.bottleneck_slot}")
        result = engine.run(signal)
        
        status = result.get("status")
        tickers_count = len(result.get("tickers", []))
        print(f" -> Status: {status}")
        print(f" -> Tickers: {tickers_count}")
        if status == "REJECT":
            print(f" -> Reason: {result.get('reject_reason')}")
        else:
            for t in result["tickers"]:
                print(f"    - {t['name']} ({len(t['evidence'])} facts)")
                
        # Save JSON
        out_path = out_dir / filename
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f" -> Saved to {out_path}")

if __name__ == "__main__":
    main()
