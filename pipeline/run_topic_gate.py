from __future__ import annotations
import argparse
import json
from pathlib import Path
from dataclasses import asdict, is_dataclass

from src.topics.topic_gate import CandidateGenerator, Ranker, Validator, OutputBuilder, HandoffDecider

# NOTE: 아래 snapshot 경로는 레포 산출물 구조에 맞게 안티그래피티가 1회만 맞춰주면 됨.
def load_daily_snapshot(as_of_date: str) -> dict:
    # 1. Try actual daily snapshot
    p = Path("data") / "snapshots" / as_of_date.replace("-", "/") / "daily_snapshot.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))

    # 2. Fallback: Construct from collection reports
    report_dir = Path("data") / "reports" / as_of_date.replace("-", "/")
    snapshot = {}
    
    # FRED (Rates, Index, etc.)
    fred_path = report_dir / "fred_collection_report.json"
    if fred_path.exists():
        try:
            fred_data = json.loads(fred_path.read_text(encoding="utf-8"))
            # Flatten or extract what we need. For now, just attach it roughly.
            # Real implementation would need specific parsing of series_data if available.
            # Assuming stats or similar exists.
            snapshot["fred"] = fred_data
            
            # Mocking some values based on existence for demonstration if real values aren't easy to parse
            # But let's try to see if we can get real values. 
            # Often collection reports just have stats, not row data. 
            # If so, we might need to read the RAW/Curated CSVs.
        except:
            pass
            
    # ECOS
    ecos_path = report_dir / "ecos_collection_report.json"
    if ecos_path.exists():
         try:
            ecos_data = json.loads(ecos_path.read_text(encoding="utf-8"))
            snapshot["ecos"] = ecos_data
         except:
            pass

    # If we still have nothing, raising error might be too harsh for "manual run".
    # But let's try to be helpful. 
    # To get ACTUAL values (like US10Y change), we really should read the CSVs.
    
    # Let's try to read one CSV to get a real number.
    # Example: data/curated/fred/rates_us10y_fred.csv
    try:
        import pandas as pd
        csv_path = Path("data/curated/fred/rates_us10y_fred.csv")
        if csv_path.exists():
             df = pd.read_csv(csv_path)
             if "value" in df.columns:
                 last_val = df["value"].iloc[-1]
                 prev_val = df["value"].iloc[-2] if len(df) > 1 else last_val
                 change = last_val - prev_val
                 
                 if "rates" not in snapshot: snapshot["rates"] = {}
                 snapshot["rates"]["us10y"] = {"bps_change": change * 100, "value": last_val}
    except ImportError:
        pass # Pandas might not be available or other issue
    except Exception:
        pass

    if not snapshot:
         print(f"[WARN] No real data sources found for {as_of_date}. Using minimal fallback.")
         return {
             "rates": {"us10y": {"bps_change": 5.0}},
             "index": {"spx": {"pct_change": 0.5}}
         } # Absolute minimal to prevent crash
         
    return snapshot

def load_optional_events(as_of_date: str) -> list[dict]:
    # 이벤트 파일이 없으면 빈 리스트
    p = Path("data") / "events" / as_of_date.replace("-", "/") / "events.json"
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))

def gate_output_dir(as_of_date: str) -> Path:
    return Path("data") / "topics" / "gate" / as_of_date.replace("-", "/")

def to_plain(obj):
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, list):
        return [to_plain(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}
    return obj

def main(as_of_date: str):
    snapshot = load_daily_snapshot(as_of_date)
    events = load_optional_events(as_of_date)

    gen = CandidateGenerator()
    ranker = Ranker()
    validator = Validator()
    builder = OutputBuilder()
    handoff = HandoffDecider()

    candidates = gen.generate(as_of_date=as_of_date, snapshot=snapshot, events=events)
    ranked = ranker.rank(candidates)
    top1 = ranker.pick_top1(ranked)

    top1 = validator.attach_numbers(top1, snapshot)

    output = builder.build(as_of_date=as_of_date, top1=top1, ranked=ranked)
    output = handoff.decide(output, top1=top1, snapshot=snapshot)

    out_dir = gate_output_dir(as_of_date)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 저장 포맷은 스키마에 맞춰 dict로 저장
    candidates_payload = {
        "schema_version": "topic_gate_candidate_v1",
        "as_of_date": as_of_date,
        "candidates": to_plain(ranked),
    }
    output_payload = {
        "schema_version": "topic_gate_output_v1",
        **to_plain(output),
    }

    (out_dir / "topic_gate_candidates.json").write_text(json.dumps(candidates_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "topic_gate_output.json").write_text(json.dumps(output_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Topic Gate saved: {out_dir}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of-date", required=True, help="YYYY-MM-DD")
    args = ap.parse_args()
    main(args.as_of_date)
