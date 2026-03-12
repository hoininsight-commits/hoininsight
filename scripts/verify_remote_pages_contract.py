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
    req = urllib.request.Request(f"{url}?v={int(time.time())}", headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            if response.getcode() != 200: 
                print(f"⚠️ fetch_json: HTTP {response.getcode()} for {url}")
                return None
            return json.loads(response.read().decode('utf-8'))
    except Exception as e: 
        print(f"⚠️ fetch_json: Error fetching {url}: {e}")
        return None

def main():
    print("REMOTE DEPLOY VERIFICATION (PHASE-22A)")
    
    max_retries = 10
    for attempt in range(1, max_retries + 1):
        print(f"--- Attempt {attempt}/{max_retries} ---")
        valid = True
        
        # Manifest & Today
        m_url = "https://hoininsight-commits.github.io/hoininsight/data/decision/manifest.json"
        t_url = "https://hoininsight-commits.github.io/hoininsight/data/decision/today.json"
        m_data, t_data = fetch_json(m_url), fetch_json(t_url)
        
        if not m_data or not t_data: valid = False; print("❌ manifest or today.json missing")
        else:
            gen_time = m_data.get('generated_at', '')
            print(f"✅ manifest and today.json parsed. Remote Time: {gen_time}")
            
            # Freshness Check (PHASE-22A Hardening)
            current_date_utc = time.strftime("%Y-%m-%d", time.gmtime())
            if current_date_utc not in gen_time:
                valid = False
                print(f"⚠️ Remote data is STALE (Expected: {current_date_utc}, Found: {gen_time}). Waiting for GH Pages sync...")
            
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

        # [STEP-16] Video Stock Mentionables (Subsumed Linkage Pack)
        l_url = "https://hoininsight-commits.github.io/hoininsight/data/decision/mentionables.json"
        l_data = fetch_json(l_url)
        if not l_data: valid = False; print("❌ mentionables.json missing")
        else:
            mention_count = len(l_data.get("mentionables", []))
            print(f"✅ Stock mentionables parsed. Count: {mention_count}")
            # [Relaxation] Allow zero mentionables on quiet days if valid
            # But the engine usually finds a sector fallback

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
        req_b = urllib.request.Request(f"{b_url}?v={int(time.time())}", headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req_b, context=ctx, timeout=10) as resp_b:
                if resp_b.getcode() == 200: print("✅ OS brief (markdown) found")
                else: valid = False; print(f"❌ investment_os_brief.md found but code {resp_b.getcode()}")
        except Exception as e: valid = False; print(f"❌ investment_os_brief.md missing: {e}")

        # [PHASE-25] Strategic Capital Allocation Layer
        ca_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/capital_allocation_state.json"
        ca_data = fetch_json(ca_url)
        if not ca_data: valid = False; print("❌ capital_allocation_state.json missing")
        else:
            print(f"✅ Capital Allocation parsed. Mode: {ca_data.get('allocation_profile', {}).get('mode')}")
            if not ca_data.get("framework", {}).get("core_bucket"): valid = False; print("❌ core_bucket missing")

        cab_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/capital_allocation_brief.md"
        req_cab = urllib.request.Request(f"{cab_url}?v={int(time.time())}", headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req_cab, context=ctx, timeout=10) as resp_cab:
                if resp_cab.getcode() == 200: print("✅ Capital Allocation brief (markdown) found")
                else: valid = False; print(f"❌ capital_allocation_brief.md found but code {resp_cab.getcode()}")
        except Exception as e: valid = False; print(f"❌ capital_allocation_brief.md missing: {e}")

        # [PHASE-26] Structural Timing Layer
        tm_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/timing_state.json"
        tm_data = fetch_json(tm_url)
        if not tm_data: valid = False; print("❌ timing_state.json missing")
        else:
            print(f"✅ Timing State parsed. Gear: {tm_data.get('timing_gear', {}).get('level')}")
            if not tm_data.get("timing_gear", {}).get("label"): valid = False; print("❌ timing label missing")

        tmb_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/timing_brief.md"
        req_tmb = urllib.request.Request(f"{tmb_url}?v={int(time.time())}", headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req_tmb, context=ctx, timeout=10) as resp_tmb:
                if resp_tmb.getcode() == 200: print("✅ Timing brief (markdown) found")
                else: valid = False; print(f"❌ timing_brief.md found but code {resp_tmb.getcode()}")
        except Exception as e: valid = False; print(f"❌ timing_brief.md missing: {e}")

        # [PHASE-27] Structural Probability Compression Layer
        pc_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/probability_compression_state.json"
        pc_data = fetch_json(pc_url)
        if not pc_data: valid = False; print("❌ probability_compression_state.json missing")
        else:
            print(f"✅ Compression State parsed. Direction: {pc_data.get('compression_state', {}).get('direction')}")
            if not pc_data.get("scenario_tree", {}).get("primary_path"): valid = False; print("❌ primary_path missing")

        pcb_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/probability_compression_brief.md"
        req_pcb = urllib.request.Request(f"{pcb_url}?v={int(time.time())}", headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req_pcb, context=ctx, timeout=10) as resp_pcb:
                if resp_pcb.getcode() == 200: print("✅ Probability Compression brief (markdown) found")
                else: valid = False; print(f"❌ probability_compression_brief.md found but code {resp_pcb.getcode()}")
        except Exception as e: valid = False; print(f"❌ probability_compression_brief.md missing: {e}")

        # [PHASE-28] Structural Meta-Volatility Layer
        mv_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/meta_volatility_state.json"
        mv_data = fetch_json(mv_url)
        if not mv_data: valid = False; print("❌ meta_volatility_state.json missing")
        else:
            print(f"✅ Meta-Volatility parsed. Mode: {mv_data.get('state', {}).get('mode')}")
            if not mv_data.get("interpretation", {}).get("one_liner"): valid = False; print("❌ one_liner missing")

        mvb_url = "https://hoininsight-commits.github.io/hoininsight/data/ops/meta_volatility_brief.md"
        req_mvb = urllib.request.Request(f"{mvb_url}?v={int(time.time())}", headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req_mvb, context=ctx, timeout=10) as resp_mvb:
                if resp_mvb.getcode() == 200: print("✅ Meta-Volatility brief (markdown) found")
                else: valid = False; print(f"❌ meta_volatility_brief.md found but code {resp_mvb.getcode()}")
        except Exception as e: valid = False; print(f"❌ meta_volatility_brief.md missing: {e}")

        if valid: print("✅ Remote Contract Verification PASSED."); sys.exit(0)
        print("⚠️ Verification rejected. Waiting 20 seconds..."); time.sleep(20)

    print("❌ Remote Contract Verification FAILED."); sys.exit(1)

if __name__ == "__main__":
    main()
