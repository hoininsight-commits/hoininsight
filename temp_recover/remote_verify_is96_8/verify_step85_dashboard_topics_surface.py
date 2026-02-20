import json
import os
from pathlib import Path

def verify_step85():
    base_dir = Path(".")
    topics_root = base_dir / "docs/dashboard/topics"
    index_path = topics_root / "index.json"
    items_dir = topics_root / "items"

    print("--- STEP 85 Verification ---")

    # 1. Check index.json
    if not index_path.exists():
        print("❌ FAIL: docs/dashboard/topics/index.json missing")
        return False
    print("✅ OK: docs/dashboard/topics/index.json exists")

    index_data = json.loads(index_path.read_text(encoding='utf-8'))
    if not index_data or not isinstance(index_data, list):
        print("❌ FAIL: docs/dashboard/topics/index.json is empty or not a list")
        return False
    print(f"✅ OK: index.json contains {len(index_data)} entries")

    # 2. Check top1.json
    latest_entry = index_data[0]
    item_path = base_dir / "docs/dashboard" / latest_entry["path"]
    if not item_path.exists():
        print(f"❌ FAIL: {item_path} missing")
        return False
    print(f"✅ OK: {item_path} exists")

    # 3. Check 필수 키 (date, rank, title, why_now, badges)
    item_data = json.loads(item_path.read_text(encoding='utf-8'))
    required_keys = ["date", "rank", "title", "why_now", "badges"]
    missing_keys = [k for k in required_keys if k not in item_data]
    if missing_keys:
        print(f"❌ FAIL: Missing mandatory keys in JSON: {missing_keys}")
        return False
    print("✅ OK: Mandatory keys present in top1.json")

    # 4. Check dashboard HTML (simple check)
    dashboard_html = base_dir / "dashboard/index.html"
    if dashboard_html.exists():
        content = dashboard_html.read_text(encoding='utf-8')
        # Since titles change, we can't check for exact title, 
        # but we can check for the new CSS class 'top1' or the section title
        if ' 오늘의 TOP-1 핵심' in content or 'topic-card top1' in content:
            print("✅ OK: Dashboard HTML contains Top-1 section/class")
        else:
            print("⚠️ WARN: Dashboard HTML does not contain Top-1 section (might need generation)")
    else:
        print("⚠️ WARN: dashboard/index.html missing")

    print("\n--- Verification Completed Successfully ---")
    return True

if __name__ == "__main__":
    verify_step85()
