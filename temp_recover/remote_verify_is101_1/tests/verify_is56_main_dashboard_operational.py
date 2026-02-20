import sys
from pathlib import Path

def test_dashboard_ops():
    print("[TEST] Verifying IS-56 Main Dashboard Operational Lock...")
    base_dir = Path(".")
    index_path = base_dir / "dashboard" / "index.html"
    
    if not index_path.exists():
        print("[FAIL] Dashboard index.html not found.")
        sys.exit(1)
        
    html = index_path.read_text(encoding='utf-8')
    
    # 1. Check Pinned Section Title (Korean)
    if "오늘의 확정 토픽" not in html and "오늘 발화할 토픽 없음" not in html:
        print("[FAIL] Pinned Topic header (Korean) not found.")
        sys.exit(1)
        
    # 2. Check Content Package Headers
    if "콘텐츠 패키지" not in html and "오늘 발화할 토픽 없음" not in html:
         print("[FAIL] Content Package header not found.")
         sys.exit(1)
         
    # 3. Check Copy Buttons
    if "복사하기" not in html and "오늘 발화할 토픽 없음" not in html:
         print("[FAIL] Copy buttons not found.")
         sys.exit(1)

    print("[PASS] IS-56 Dashboard Operation Mode verified.")

if __name__ == "__main__":
    test_dashboard_ops()
