import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Configure Logger
logger = logging.getLogger("FactFirstLoader")

REQUIRED_FIELDS = ["fact_id", "type", "date", "subject", "object", "fact", "source", "confidence"]
VALID_TYPES = ["FLOW", "POLICY", "STRUCTURE"]
VALID_CONFIDENCE = ["HIGH", "MEDIUM", "LOW"]

def load_fact_first_input(base_dir: Path, target_date_kst: str) -> Dict[str, Any]:
    """
    Load operator-provided facts from data/facts/fact_first/{DATE}.json
    
    Args:
        base_dir: Project root directory
        target_date_kst: YYYY-MM-DD string (KST)
        
    Returns:
        Dict containing:
        - run_date
        - count
        - counts_by_type
        - facts (list of validated dicts)
        - errors (list of error dicts)
    """
    input_path = base_dir / "data" / "facts" / "fact_first" / f"{target_date_kst}.json"
    output_json_path = base_dir / "data" / "ops" / "fact_first_input_today.json"
    output_md_path = base_dir / "data" / "ops" / "fact_first_input_today.md"
    
    # Ensure output dir exists
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    
    result = {
        "run_date": target_date_kst,
        "count": 0,
        "counts_by_type": {"FLOW": 0, "POLICY": 0, "STRUCTURE": 0},
        "facts": [],
        "errors": []
    }
    
    if not input_path.exists():
        logger.warning(f"Fact input file missing: {input_path}")
        result["errors"].append({"message": "Input file not found", "path": str(input_path)})
        _write_outputs(result, output_json_path, output_md_path)
        return result
        
    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        result["errors"].append({"message": f"Invalid JSON format: {str(e)}", "path": str(input_path)})
        _write_outputs(result, output_json_path, output_md_path)
        return result
        
    if not isinstance(data, list):
        # Maybe wrapped in a key? operator might put {"facts": [...]} 
        # But spec implies list of records. Let's support list directly.
        if isinstance(data, dict) and "facts" in data and isinstance(data["facts"], list):
            data = data["facts"]
        else:
            result["errors"].append({"message": "Root must be a list or dict with 'facts' list"})
            _write_outputs(result, output_json_path, output_md_path)
            return result

    validated_facts = []
    seen_keys = set()
    
    for idx, row in enumerate(data):
        # 1. Check Required Fields
        missing = [f for f in REQUIRED_FIELDS if f not in row]
        if missing:
            result["errors"].append({"row_index": idx, "message": f"Missing fields: {missing}"})
            continue
            
        # 2. Validate Enums
        if row["type"] not in VALID_TYPES:
            result["errors"].append({"row_index": idx, "message": f"Invalid type: {row['type']}"})
            continue
            
        if row["confidence"] not in VALID_CONFIDENCE:
            result["errors"].append({"row_index": idx, "message": f"Invalid confidence: {row['confidence']}"})
            continue
            
        # 3. Deduplication (type, subject, object, fact)
        # Using a tuple key
        dedup_key = (row["type"], row["subject"], row["object"], row["fact"])
        if dedup_key in seen_keys:
            continue # Skip duplicate silently or log? Spec says "determinstic", keeping first.
        
        seen_keys.add(dedup_key)
        
        # Add to valid list
        validated_facts.append(row)
        result["counts_by_type"][row["type"]] += 1
        
    result["facts"] = validated_facts
    result["count"] = len(validated_facts)
    
    _write_outputs(result, output_json_path, output_md_path)
    return result

def _write_outputs(result: Dict, json_path: Path, md_path: Path):
    # Write JSON
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Write MD
    md_lines = [
        f"# Fact-First Input Summary ({result['run_date']})",
        f"",
        f"- **Total Facts**: {result['count']}",
        f"- **Flow**: {result['counts_by_type']['FLOW']}",
        f"- **Policy**: {result['counts_by_type']['POLICY']}",
        f"- **Structure**: {result['counts_by_type']['STRUCTURE']}",
        f"",
        "## Errors",
    ]
    
    if result["errors"]:
        for e in result["errors"][:5]: # Show first 5
            md_lines.append(f"- {e}")
        if len(result["errors"]) > 5:
            md_lines.append(f"- ... and {len(result['errors']) - 5} more")
    else:
        md_lines.append("No errors.")
        
    md_lines.append("")
    md_lines.append("## Valid Facts (Top 10)")
    md_lines.append("| Type | Subject -> Object | Fact | Source |")
    md_lines.append("|---|---|---|---|")
    
    for f in result["facts"][:10]:
        md_lines.append(f"| {f['type']} | {f['subject']} -> {f['object']} | {f['fact']} | {f['source']} |")
        
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
