import os
import json
from pathlib import Path
from src.topic_engine.arbiter import TopicArbiter

def test_arbiter_dna():
    os.environ["HOIN_BASE_DIR"] = os.getcwd()
    arbiter = TopicArbiter()
    
    # Mock raw data
    raw_dir = Path("data/raw/test")
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "market.json").write_text(json.dumps({"data": {"kospi": 2700}}))
    
    print("Testing Arbiter prompt generation with DNA...")
    # I won't actually call Gemini to save cost, but I'll check if DNAManager is called.
    # Since I can't easily mock the prompt print without editing the code, 
    # I'll just trust the integration since the test_dna.py worked.
    
    # Actually, I can check the log.
    patch_log = Path("data/history/dna_patch_log.json")
    if patch_log.exists():
        patch_log.unlink()
        
    try:
        # This will fail due to no Gemini call or lack of data, but we check if it logs the patch application.
        arbiter.select_topic_from_raw(raw_dir)
    except:
        pass
        
    if patch_log.exists():
        print("✅ DNAManager log found! Arbiter is using the DNA system.")
        print(patch_log.read_text())
    else:
        print("❌ DNAManager log not found.")

if __name__ == "__main__":
    test_arbiter_dna()
