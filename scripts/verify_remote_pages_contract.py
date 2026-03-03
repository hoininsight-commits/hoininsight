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

        # [PHASE-22B] Video Stock Linkage Pack
        l_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/stock_linkage_pack.json"
        l_data = fetch_json(l_url)
        if not l_data: valid = False; print("❌ stock_linkage_pack.json missing")
        else:
            topics_count = len(l_data.get("topics", []))
            print(f"✅ Stock linkage parsed. Topics: {topics_count}")
            if topics_count == 0: valid = False; print("❌ linkage topics empty")

        # [PHASE-22C] Video Conflict Density Pack
        d_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/conflict_density_pack.json"
        d_data = fetch_json(d_url)
        if not d_data: valid = False; print("❌ conflict_density_pack.json missing")
        else:
            topics_count = len(d_data.get("topics", []))
            print(f"✅ Conflict density parsed. Topics: {topics_count}")
            if topics_count == 0: valid = False; print("❌ density topics empty")
            for t in d_data.get("topics", []):
                p = t.get("density_text", {}).get("structured_paragraph", [])
                if len(p) < 3: valid = False; print(f"❌ paragraph density low for {t.get('dataset_id')}")

        # [PHASE-23] Structural Regime State
        r_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/regime_state.json"
        r_data = fetch_json(r_url)
        if not r_data: valid = False; print("❌ regime_state.json missing")
        else:
            print(f"✅ Regime state parsed. State: {r_data.get('regime', {}).get('liquidity_state')}")
            if not r_data.get("regime", {}).get("policy_state"): valid = False; print("❌ policy_state missing")
            if len(r_data.get("evidence", [])) < 1: valid = False; print("❌ evidence empty")

        # [PHASE-24] Investment OS Layer
        o_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/investment_os_state.json"
        o_data = fetch_json(o_url)
        if not o_data: valid = False; print("❌ investment_os_state.json missing")
        else:
            print(f"✅ OS state parsed. Stance: {o_data.get('os_summary', {}).get('stance')}")
            if len(o_data.get("priority_topics", [])) < 1: valid = False; print("❌ priority_topics empty")

        b_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/investment_os_brief.md"
        req_b = urllib.request.Request(b_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req_b, context=ssl._create_unverified_context(), timeout=10) as resp_b:
                if resp_b.getcode() == 200: print("✅ OS brief (markdown) found")
                else: valid = False; print("❌ investment_os_brief.md found but code not 200")
        except: valid = False; print("❌ investment_os_brief.md missing")

        if valid: print("✅ Remote Contract Verification PASSED."); sys.exit(0)
        print("⚠️ Verification rejected. Waiting 20 seconds..."); time.sleep(20)

    print("❌ Remote Contract Verification FAILED."); sys.exit(1)

if __name__ == "__main__":
    main()
