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
    
    # We want one commit per day (the last one of the day, i.e., highest timestamp)
    # git log outputs newest first. So the first time we see a date, it's the latest commit for that day.
    daily_commits = {}
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            h = parts[0]
            d = parts[1][:10]  # YYYY-MM-DD
            if d not in daily_commits:
                daily_commits[d] = h
                
    # return oldest first
    return sorted([(d, h) for d, h in daily_commits.items()])

def extract_topics(obj):
    if isinstance(obj, dict):
        # Heuristic: if a dict has 'title' and some score or status, it's a topic
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
    if len(sys.argv) > 1 and sys.argv[1] == "--30days":
        days = 30
        
    daily_commits = get_commits_last_n_days(days)
    print(f"Found {len(daily_commits)} daily commits to process.")
    
    topics_db = defaultdict(dict)  # (date, title) -> merged_data
    
    for date, commit_hash in daily_commits:
        print(f"Processing {date} (Commit {commit_hash[:7]})")
        
        # Get all json files in data/ops and data/decision
        cmd = f"git ls-tree -r --name-only {commit_hash}"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        files = [f for f in res.stdout.splitlines() if f.endswith('.json') and ('data/ops' in f or 'data/decision' in f)]
        
        for f in files:
            # Skip noise
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
                    
                    # Merge fields
                    key = (date, title)
                    if key not in topics_db:
                        topics_db[key] = {'date': date, 'title': title}
                        
                    for k, v in t.items():
                        if v is not None and v != "":
                            # Allow overwrite to get the latest stage state within the day
                            topics_db[key][k] = v
                            
            except json.JSONDecodeError:
                pass
                
    # Format and clean up the database
    out_list = []
    for (date, title), record in topics_db.items():
        # Map fields precisely as requested by the user
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
            'capital_flow_score': record.get('capital_flow_score', 0),
            'policy_score': record.get('policy_score', 0),
            'persistence_score': record.get('persistence_score', 0),
            'conflict_flag': record.get('conflict_flag', False),
            'expectation_gap': record.get('expectation_gap', record.get('expectation_gap_score', 0)),
            'escalation_detected': escalation,
            'video_ready': record.get('video_ready', False),
            'speakability': record.get('speakability', 'UNKNOWN'),
            'status': record.get('status', 'PENDING'),
            'why_now_type': record.get('why_now_type', record.get('why_now', 'UNKNOWN'))
        }
        out_list.append(clean_record)
        
    out_dir = Path("data_outputs/ops")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if days == 14:
        out_file = out_dir / "approval_forensics_last14days.json"
    else:
        out_file = out_dir / "economic_hunter_candidates_30days.json"
        
    out_file.write_text(json.dumps(out_list, indent=2, ensure_ascii=False))
    print(f"\nExtracted {len(out_list)} topics to {out_file}")

if __name__ == "__main__":
    main()
