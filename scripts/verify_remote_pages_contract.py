#!/usr/bin/env python3
import urllib.request
import json
import ssl
import sys
import time

def fetch_json(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            if response.getcode() != 200: return None
            return json.loads(response.read().decode('utf-8'))
    except: return None

def main():
    print("REMOTE DEPLOY VERIFICATION (PHASE-22A)")
    
    max_retries = 6
    for attempt in range(1, max_retries + 1):
        print(f"--- Attempt {attempt}/{max_retries} ---")
        valid = True
        
        # Manifest & Today
        m_url = "https://hoininsight-commits.github.io/hoininsight/data/decision/manifest.json"
        t_url = "https://hoininsight-commits.github.io/hoininsight/data/decision/today.json"
        m_data, t_data = fetch_json(m_url), fetch_json(t_url)
        
        if not m_data or not t_data: valid = False; print("❌ manifest or today.json missing")
        else:
            print(f"✅ manifest and today.json parsed. Time: {m_data.get('generated_at')}")
            
        # Video Candidate Pool
        v_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/video_candidate_pool.json"
        v_data = fetch_json(v_url)
        if not v_data: valid = False; print("❌ video_candidate_pool.json missing")
        else: print(f"✅ Video candidates: {len(v_data.get('top_candidates', []))}")
        
        # Video Script Pack
        s_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/video_script_pack.json"
        s_data = fetch_json(s_url)
        if not s_data: valid = False; print("❌ video_script_pack.json missing")
        else:
            print(f"✅ Script pack parsed. Candidates: {len(s_data.get('candidates', []))}")
            for c in s_data.get("candidates", []):
                if not c.get("script", {}).get("hook"): valid = False; print(f"❌ hook missing for {c.get('dataset_id')}")

        if valid: print("✅ Remote Contract Verification PASSED."); sys.exit(0)
        print("⚠️ Verification rejected. Waiting 20 seconds..."); time.sleep(20)

    print("❌ Remote Contract Verification FAILED."); sys.exit(1)

if __name__ == "__main__":
    main()
