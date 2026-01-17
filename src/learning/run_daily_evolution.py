
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
base_dir = Path(__file__).parent.parent.parent
sys.path.append(str(base_dir))

from src.learning.deep_logic_analyzer import DeepLogicAnalyzer

def run_daily_evolution(target_date: str = None):
    """
    Scans transcripts for the given date (default: today) and runs DeepLogicAnalyzer.
    Generates proposals and a summary report.
    """
    analyzer = DeepLogicAnalyzer(base_dir)
    
    if target_date is None:
        target_date = datetime.utcnow().strftime("%Y/%m/%d")
    
    # Handle YYYY-MM-DD format if passed
    target_date = target_date.replace("-", "/")
    
    transcript_dir = base_dir / "data/narratives/transcripts" / target_date
    proposal_dir = base_dir / "data/evolution/proposals"
    report_dir = base_dir / "data/evolution/reports" / target_date
    
    proposal_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[Evolution] Scanning transcripts in: {transcript_dir}")
    
    if not transcript_dir.exists():
        print(f"[Evolution] No transcripts found for date {target_date}")
        return

    analysis_results = []
    
    for txt_file in transcript_dir.glob("*.txt"):
        print(f"[Evolution] Analyzing: {txt_file.name}...")
        try:
            content = txt_file.read_text(encoding='utf-8')
            # Extract title properly or use filename
            title = txt_file.stem.replace("_", " ")
            
            # RUN ANALYSIS
            result = analyzer.analyze(content, title)
            
            # Add Source Info
            result['source_file'] = txt_file.name
            result['analyzed_at'] = datetime.utcnow().isoformat()
            
            analysis_results.append(result)
            
            # Save Proposals individually
            if result.get('final_decision') == "UPDATE_REQUIRED":
                for prop in result.get('proposals', []):
                    prop_id = f"EVO-{datetime.utcnow().strftime('%Y%m%d')}-{abs(hash(prop['content'])) % 100000:05d}"
                    
                    proposal_file = {
                        "id": prop_id,
                        "generated_at": datetime.utcnow().isoformat(),
                        "category": prop['category'],
                        "status": "PROPOSED",
                        "content": {
                            "condition": prop['content'],
                            "meaning": prop.get('reason', 'Automatic extraction')
                        },
                        "evidence": {
                            "quote": result.get('learned_rule', 'N/A'),
                            "source": title
                        }
                    }
                    
                    # Save
                    (proposal_dir / f"{prop_id}.json").write_text(
                        json.dumps(proposal_file, indent=2, ensure_ascii=False), 
                        encoding='utf-8'
                    )
                    print(f"   -> Saved Proposal {prop_id}")

        except Exception as e:
            print(f"[Error] Failed to analyze {txt_file.name}: {e}")

    # Save Aggregate Report for Dashboard
    report_path = report_dir / "daily_analysis_log.json"
    report_data = {
        "date": target_date,
        "total_analyzed": len(analysis_results),
        "results": analysis_results
    }
    report_path.write_text(json.dumps(report_data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"[Evolution] Saved daily analysis log to {report_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_daily_evolution(sys.argv[1])
    else:
        run_daily_evolution()
