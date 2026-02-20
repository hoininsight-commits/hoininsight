import sys
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.issuesignal.tone_lock import ToneLockCompiler

def main():
    base_dir = Path(".")
    print(f"\n[VERIFY] Starting IssueSignal Tone DNA Lock Verification (IS-20)")
    
    compiler = ToneLockCompiler(base_dir)
    
    # 1. Simulate Input Data
    trigger_data = {
        "content_summary": "엔비디아의 신규 칩 지연 소식",
        "actor": "글로벌 빅테크 기업들",
        "bottleneck": "차세대 패키징 라인"
    }
    tickers = [{"ticker": "TSM", "role": "OWNER"}]
    kill_switches = [{"ticker": "TSM", "condition": "수율 90% 돌파 공시"}]
    one_sentence = "오늘 패키징 병목 때문에 빅테크는 증설을 해야 하고, 자본은 TSM으로 이동한다."
    
    # 2. Compile Content
    print("\n[STEP 1] Compiling 7-Block Content...")
    content = compiler.compile(trigger_data, tickers, kill_switches, one_sentence)
    
    if content:
        print("\n--- Compiled Content Start ---")
        print(content)
        print("--- Compiled Content End ---")
        
        # 3. Structural Validation Check
        blocks = content.split("\n\n")
        print(f"\n[STEP 2] Validating Structure...")
        print(f" - Number of blocks: {len(blocks)} (Expected: 7)")
        
        # 4. Tone Validation Check
        print(f"\n[STEP 3] Validating Tone...")
        forbidden = ["?", "!", "일 수도", "같다", "가능성"]
        # Explicit check for speculation endings, allowing necessity (~수밖에 없다)
        found_elements = [f for f in forbidden if f in content]
        contains_forbidden = len(found_elements) > 0
        
        # Check for '수 있다' but only if not followed by '밖에'
        if "수 있다" in content:
             if "수밖에" not in content:
                 contains_forbidden = True
                 found_elements.append("수 있다")
        
        print(f" - Found forbidden elements: {found_elements}")
        print(f" - Contains forbidden elements: {contains_forbidden} (Expected: False)")
        
        if len(blocks) == 7 and not contains_forbidden:
            print("\n[VERIFY][SUCCESS] IssueSignal Tone DNA Lock (IS-20) is fully functional.")
        else:
            print("\n[VERIFY][FAIL] Structural or tone validation failed.")
    else:
        print("\n[VERIFY][FAIL] Content compilation failed or rejected by internal guards.")

if __name__ == "__main__":
    main()
