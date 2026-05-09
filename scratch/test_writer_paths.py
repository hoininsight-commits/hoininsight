import os
from src.agents.writer import WriterAgent

def test_init():
    # Set target date and round to test
    os.environ["HOIN_TARGET_DATE"] = "2026-05-09"
    os.environ["HOIN_TARGET_ROUND"] = "1"
    
    agent = WriterAgent()
    print(f"Signal Dir: {agent.signal_dir}")
    print(f"Analysis Dir: {agent.analysis_dir}")
    print(f"Script Dir: {agent.script_dir}")
    
    # Expected: data/scripts/2026/05/09/Round_1
    expected = "data/scripts/2026/05/09/Round_1"
    if str(agent.script_dir) == expected:
        print("✅ Path matched expected format!")
    else:
        print(f"❌ Path mismatch! Expected {expected}, got {agent.script_dir}")

if __name__ == "__main__":
    test_init()
