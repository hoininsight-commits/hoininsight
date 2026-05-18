from src.utils.dna_manager import DNAManager
from pathlib import Path

def test_dna():
    manager = DNAManager()
    patch = manager.get_latest_dna_patch(limit=3)
    print("--- LATEST DNA PATCH ---")
    print(patch)
    print("------------------------")
    
    manager.log_patch_application("TEST_AGENT")
    print("Log recorded.")

if __name__ == "__main__":
    test_dna()
