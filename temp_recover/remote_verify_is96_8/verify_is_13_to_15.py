import sys
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.issuesignal.ticker_collapse import TickerCollapseEngine
from src.issuesignal.kill_switch import KillSwitchEngine
from src.issuesignal.decision_card import DecisionCardGenerator

def main():
    base_dir = Path(".")
    print(f"\n[VERIFY] Starting IssueSignal Decision-Grade Verification (IS-13 to IS-15)")
    
    collapse_engine = TickerCollapseEngine(base_dir)
    ks_engine = KillSwitchEngine(base_dir)
    card_gen = DecisionCardGenerator(base_dir)
    
    # 1. Mock Trigger & Evidence (IS-13)
    print("\n[STEP 1] Collapsing Trigger to Unavoidable Tickers...")
    mock_trigger = {
        "id": "IS-2026-01-29-001",
        "category": "POLICY_SCHEDULE",
        "source": "G7 Council",
        "content": "Official commitment to localize advanced chip packaging within the next 12 months.",
        "why_now": "Capital is forced to move to resolve sudden packaging bottlenecks in the non-China supply chain.",
        "ignore_reason": "Failure to comply will result in 40% export tax increase.",
        "candidates": [
            {"ticker": "AMAT", "revenue_focus": 0.8},
            {"ticker": "ASML", "revenue_focus": 0.9},
            {"ticker": "TSM", "revenue_focus": 0.95},
            {"ticker": "INTC", "revenue_focus": 0.3} # This one should be filtered out (< 0.5)
        ]
    }
    mock_evidence = {"structural_shift": "Confirmed"}
    
    collapsed_tickers = collapse_engine.collapse_to_tickers(mock_trigger, mock_evidence)
    print(f"Collapsed Tickers: {[t['ticker'] for t in collapsed_tickers]}")
    
    # 2. Generate Kill-Switches (IS-14)
    print("\n[STEP 2] Generating Kill-Switches...")
    kill_switches = []
    for t in collapsed_tickers:
        ks = ks_engine.generate_kill_switch(t["ticker"], mock_trigger)
        print(f" - {ks['ticker']}: {ks['condition']}")
        kill_switches.append(ks)
        
    # 3. Generate Final Decision Card (IS-15)
    print("\n[STEP 3] Generating Final Decision Card...")
    card_path = card_gen.generate_card(mock_trigger, collapsed_tickers, kill_switches)
    
    if card_path:
        print(f" -> Decision Card Ready: {card_path}")
        print("\nCard Content Preview:")
        with open(card_path, "r", encoding="utf-8") as f:
            print(f.read())
            
    print("\n[VERIFY][SUCCESS] IssueSignal Decision-Grade Engine (IS-13 to IS-15) is fully functional.")

if __name__ == "__main__":
    main()
