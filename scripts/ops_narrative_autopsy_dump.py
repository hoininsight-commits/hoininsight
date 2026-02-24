#!/usr/bin/env python3
import subprocess
import json
import sys
from collections import defaultdict
from pathlib import Path

def get_commits_last_n_days(days=14):
    print(f"Fetching commits from the last {days} days...")
    cmd = f'git log --since="{days} days ago" --format="%H %aI"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    lines = res.stdout.strip().splitlines()
    
    daily_commits = {}
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            h = parts[0]
            d = parts[1][:10]  # YYYY-MM-DD
            if d not in daily_commits:
                daily_commits[d] = h
                
    return sorted([(d, h) for d, h in daily_commits.items()])

def extract_topics(obj):
    if isinstance(obj, dict):
        keys = set(obj.keys())
        if 'title' in keys and ('status' in keys or 'narrative_score' in keys or 'score' in keys or 'intensity' in keys or 'speakability' in keys or 'escalation_flag' in keys):
            yield obj
        for v in obj.values():
            yield from extract_topics(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from extract_topics(item)

def main():
    days = 14
        
    daily_commits = get_commits_last_n_days(days)
    print(f"Found {len(daily_commits)} daily commits to process.")
    
    topics_db = defaultdict(dict)  # (date, title) -> merged_data
    
    for date, commit_hash in daily_commits:
        print(f"Processing {date} (Commit {commit_hash[:7]})")
        
        cmd = f"git ls-tree -r --name-only {commit_hash}"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        files = [f for f in res.stdout.splitlines() if f.endswith('.json') and ('data/ops' in f or 'data/decision' in f)]
        
        for f in files:
            if 'health' in f or 'metrics' in f or 'scoreboard' in f or 'freshness' in f or 'calibration' in f:
                continue
                
            cmd_show = f"git show {commit_hash}:{f}"
            res_show = subprocess.run(cmd_show, shell=True, capture_output=True, text=True)
            if res_show.returncode != 0:
                continue
                
            try:
                data = json.loads(res_show.stdout)
                for t in extract_topics(data):
                    title = t.get('title')
                    if not title:
                        continue
                    
                    key = (date, title)
                    if key not in topics_db:
                        topics_db[key] = {'date': date, 'title': title}
                        
                    for k, v in t.items():
                        if v is not None and v != "":
                            topics_db[key][k] = v
                            
            except json.JSONDecodeError:
                pass
                
    out_list = []
    for (date, title), record in topics_db.items():
        intensity = record.get('intensity', record.get('score', record.get('severity', 0)))
        actor_score = record.get('structural_actor_score', record.get('actor_tier_score', 0))
        escalation = record.get('escalation_detected', record.get('escalation_flag', False))
        
        clean_record = {
            'date': record.get('date'),
            'title': record.get('title', ''),
            'intensity': intensity,
            'narrative_score': record.get('narrative_score', 0),
            'final_narrative_score': record.get('final_narrative_score', record.get('narrative_score', 0)),
            'structural_actor_score': actor_score,
            'actor_tier_score': actor_score,  # requested explicitly
            'capital_flow_score': record.get('capital_flow_score', 0),
            'policy_score': record.get('policy_score', 0),
            'persistence_score': record.get('persistence_score', 0),
            'cross_axis_count': record.get('cross_axis_count', 0),
            'cross_axis_multiplier': record.get('cross_axis_multiplier', 0),
            'escalation_detected': escalation,
            'conflict_flag': record.get('conflict_flag', False),
            'expectation_gap_level': record.get('expectation_gap_level', record.get('expectation_gap', 'UNKNOWN')),
            'why_now_type': record.get('why_now_type', record.get('why_now', 'UNKNOWN'))
        }
        
        # Track if native fields were actually present or defaulted (for Step 5 Invocation Check)
        clean_record['_has_narrative_score'] = 'narrative_score' in record
        
        out_list.append(clean_record)
        
    out_dir = Path("data_outputs/ops")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    out_file = out_dir / "narrative_component_autopsy_last14days.json"
    out_file.write_text(json.dumps(out_list, indent=2, ensure_ascii=False))
    print(f"\nExtracted {len(out_list)} topics to {out_file}")

if __name__ == "__main__":
    main()
