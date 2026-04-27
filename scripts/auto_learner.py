
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.agents.learner_agent import LearnerAgent

def get_current_round():
    """
    Determines round based on current hour:
    23, 0-4  -> Round 1 (Prep for 00:00)
    5-10     -> Round 2 (Prep for 06:00)
    11-16    -> Round 3 (Prep for 12:00)
    17-22    -> Round 4 (Prep for 18:00)
    """
    hour = datetime.now().hour
    if hour >= 23 or hour < 5:
        return 1
    elif 5 <= hour < 11:
        return 2
    elif 11 <= hour < 17:
        return 3
    else:
        return 4

if __name__ == "__main__":
    print(f"🚀 Automated YouTube Learner starting at {datetime.now()}")
    current_round = get_current_round()
    
    agent = LearnerAgent()
    agent.run_evolution_loop(run_round=current_round)
    print(f"✅ Round {current_round} YouTube collection complete.")
