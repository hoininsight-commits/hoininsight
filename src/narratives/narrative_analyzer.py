"""
Phase 31-B: Narrative Analyzer
Extracts Topic Candidates and WHY NOW signals from YouTube transcripts.
Generates proposal-only outputs without modifying engine logic.

SAFETY CONSTRAINTS:
- NO Topic/MetaTopic/Regime generation
- NO automatic updates to definitions or schemas
- All outputs are "Review Required (Proposal)" status only
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# [UPDATE] Use Dynamic Knowledge Base
from src.utils.knowledge_base import KnowledgeBase
from src.learning.deep_logic_analyzer import DeepLogicAnalyzer

def _get_utc_ymd(delta_days: int = 0) -> str:
    """Get UTC date with delta."""
    d = datetime.utcnow() - timedelta(days=delta_days)
    return d.strftime("%Y/%m/%d")

def load_transcript(transcript_path: Path) -> str:
    """Load transcript text from file."""
    if not transcript_path.exists():
        return ""
    return transcript_path.read_text(encoding="utf-8")


def load_video_metadata(video_dir: Path) -> Optional[Dict[str, Any]]:
    """Load video metadata from metadata.json."""
    meta_path = video_dir / "metadata.json"
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def extract_topic_candidates(transcript: str, kb: KnowledgeBase) -> List[Dict[str, Any]]:
    """
    Extract topic candidates from transcript using Logic from Documentation.
    """
    # [UPDATE] Get dynamic keywords from Data Collection Master
    keywords = kb.get_keywords_for_extraction()
    
    candidates = []
    
    # Split transcript into sentences
    sentences = re.split(r'[.!?]\s+', transcript)
    
    # Track keyword frequency
    keyword_counts = {}
    keyword_contexts = {}
    
    for sentence in sentences:
        for keyword in keywords:
            if keyword in sentence:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
                if keyword not in keyword_contexts:
                    keyword_contexts[keyword] = []
                keyword_contexts[keyword].append(sentence.strip())
    
    # Extract top candidates (mentioned 2+ times)
    for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
        if count >= 2:
            # Extract WHY NOW clues from context
            why_now_clues = extract_why_now_clues_from_sentences(keyword_contexts[keyword])
            
            candidates.append({
                "topic": keyword,
                "evidence_quotes": keyword_contexts[keyword][:3],  # Top 3 mentions
                "why_now_clues": why_now_clues
            })
    
    # Filter: Only return candidates that have valid WHY NOW clues if possible, or top count
    # Return top 5
    return candidates[:5]


def extract_why_now_clues_from_sentences(sentences: List[str]) -> List[str]:
    """Extract WHY NOW temporal markers and triggers from sentences."""
    clues = []
    
    # Temporal markers
    temporal_markers = [
        "지금", "최근", "이번 달", "이번 주", "오늘", "곧",
        "최근 데이터", "최신", "현재", "당장", "바로 지금", "이번에"
    ]
    
    # Trigger words (Can be expanded by Logic File scanning too, but kept heuristic for speed)
    trigger_words = [
        "급등", "급락", "폭등", "폭락", "급격히", "갑자기",
        "처음으로", "사상 처음", "역대", "최고", "최저",
        "돌파", "붕괴", "임계", "전환", "변곡",
        "발표", "정책", "결정", "조치", "개입", "성명"
    ]
    
    for sentence in sentences:
        # Check for temporal markers
        for marker in temporal_markers:
            if marker in sentence:
                clues.append(f"시점: {sentence.strip()}")
                break
        
        # Check for trigger words
        for trigger in trigger_words:
            if trigger in sentence:
                clues.append(f"촉발: {sentence.strip()}")
                break
    
    return list(set(clues))[:5]  # Deduplicate and limit


def suggest_engine_mapping_hints(candidates: List[Dict[str, Any]], kb: KnowledgeBase) -> Dict[str, List[str]]:
    """
    Suggest potential DATA_COLLECTION_MASTER axes and ANOMALY_DETECTION_LOGIC triggers
    by cross-referencing extracted topics with documentation.
    """
    data_axes = set()
    anomaly_map = set()
    
    data_defs = kb.get_data_definitions()
    anomaly_logic = kb.get_anomaly_logic()
    
    for candidate in candidates:
        topic = candidate.get("topic", "")
        
        # 1. Match against Data Master
        for d in data_defs:
            # If topic matches data name or category
            if topic in d['name'] or topic in d['category']:
                # Suggest standardized name
                data_axes.add(f"{d['category']} > {d['name']}")
                
        # 2. Match against Anomaly Logic
        for logic in anomaly_logic:
            # If logic condition mentions topic (e.g. topic="금리" and logic condition contains "금리")
            if topic in logic['condition'] or topic in logic['title']:
                anomaly_map.add(f"[{logic['title']}] {logic['meaning']}")
                
    return {
        "data_axes_matches": sorted(list(data_axes)),
        "anomaly_logic_matches": sorted(list(anomaly_map))
    }


def analyze_transcript(transcript_path: Path, video_meta: Dict[str, Any], kb: KnowledgeBase) -> Dict[str, Any]:
    """
    Main analysis function using KnowledgeBase.
    """
    transcript = load_transcript(transcript_path)
    
    if not transcript:
        return {
            "topic_candidates": [],
            "engine_mapping_hints": {}
        }
    
    # Extract topic candidates
    candidates = extract_topic_candidates(transcript, kb)
    
    # Generate engine mapping hints
    hints = suggest_engine_mapping_hints(candidates, kb)
    
    return {
        "topic_candidates": candidates,
        "engine_mapping_hints": hints
    }


def generate_signal_json(video_meta: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate signal JSON output."""
    return {
        "video_id": video_meta.get("video_id", "unknown"),
        "title": video_meta.get("title", "Unknown"),
        "published_at": video_meta.get("published_at", ""),
        "topic_candidates": analysis.get("topic_candidates", []),
        "engine_mapping_hints": analysis.get("engine_mapping_hints", {}),
        "analyzer_version": "v2_dynamic_kb",
        "note": "Generated by reading official documentation (Data Master & Anomaly Logic)."
    }


def generate_proposal_markdown(video_meta: Dict[str, Any], analysis: Dict[str, Any]) -> str:
    """Generate proposal markdown output."""
    lines = []
    
    lines.append("# Narrative Proposal (Dynamic KB Driven)")
    lines.append("")
    lines.append("## Source")
    lines.append(f"- Video: {video_meta.get('title', 'Unknown')}")
    lines.append(f"- URL: https://www.youtube.com/watch?v={video_meta.get('video_id', '')}")
    lines.append(f"- Published at: {video_meta.get('published_at', 'Unknown')}")
    lines.append("")
    
    lines.append("## Topic Candidates (Extracted from Docs Matches)")
    candidates = analysis.get("topic_candidates", [])
    if candidates:
        for candidate in candidates:
            lines.append(f"- **{candidate.get('topic', 'Unknown')}**")
            # quotes
            for q in candidate.get('evidence_quotes', [])[:1]:
               lines.append(f"  - quote: \"{q[:80]}...\"")
    else:
        lines.append("- (No candidates extracted)")
    lines.append("")
    
    lines.append("## WHY NOW Signals")
    found = False
    for candidate in candidates:
        for clue in candidate.get("why_now_clues", []):
            lines.append(f"- {candidate['topic']}: {clue}")
            found = True
    if not found:
        lines.append("- (No explicit WHY NOW signals)")
    lines.append("")
    
    lines.append("## Documentation Matches (Engine Logic)")
    hints = analysis.get("engine_mapping_hints", {})
    
    lines.append("### Data Collection Master Matches")
    if hints.get("data_axes_matches"):
        for m in hints["data_axes_matches"]:
            lines.append(f"- {m}")
    else:
        lines.append("- (No direct data axis match)")
    lines.append("")
    
    lines.append("### Anomaly Detection Logic Matches")
    if hints.get("anomaly_logic_matches"):
        for m in hints["anomaly_logic_matches"]:
            lines.append(f"- {m}")
    else:
        lines.append("- (No logic pattern match)")
    lines.append("")
    
    lines.append("## Safety Notice")
    lines.append("This proposal is generated by analyzing `DATA_COLLECTION_MASTER.md` and `ANOMALY_DETECTION_LOGIC.md`.")
    return "\n".join(lines)


def process_all_transcripts(base_dir: Path) -> int:
    """
    Process all transcripts from recent collection.
    """
    # Initialize KnowledgeBase
    docs_dir = base_dir / "docs"
    kb = KnowledgeBase(docs_dir)
    kb.load()  # Parse MD files
    print(f"[Phase 31-B] Knowledge Base Loaded: {len(kb.get_data_definitions())} Data defs, {len(kb.get_anomaly_logic())} Logic patterns")
    
    # Initialize Deep Analyzer
    deep_analyzer = DeepLogicAnalyzer(kb)
    
    proposal_count = 0
    LOOKBACK = 3
    
    for i in range(LOOKBACK + 1):
        ymd = _get_utc_ymd(i)
        transcripts_dir = base_dir / "data" / "narratives" / "transcripts" / ymd
        
        if not transcripts_dir.exists():
            continue
            
        # Create output directories per date
        analysis_dir = base_dir / "data" / "narratives" / "analysis" / ymd
        proposals_dir = base_dir / "data" / "narratives" / "proposals" / ymd
        deep_dir = base_dir / "data" / "narratives" / "deep_analysis" / ymd
        
        analysis_dir.mkdir(parents=True, exist_ok=True)
        proposals_dir.mkdir(parents=True, exist_ok=True)
        deep_dir.mkdir(parents=True, exist_ok=True)
        
        for transcript_file in transcripts_dir.glob("*.txt"):
            try:
                # Skip if proposal already exists
                video_id = transcript_file.stem
                proposal_path = proposals_dir / f"proposal_{video_id}.md"
                if proposal_path.exists():
                    continue

                raw_dir = base_dir / "data" / "narratives" / "raw" / "youtube"
                video_meta = None
                
                for video_dir in raw_dir.rglob("*"):
                    if video_dir.is_dir() and video_dir.name == video_id:
                        video_meta = load_video_metadata(video_dir)
                        if video_meta:
                            break
                
                if not video_meta:
                    continue
                
                # Analyze
                analysis = analyze_transcript(transcript_file, video_meta, kb)
                
                signal_json = generate_signal_json(video_meta, analysis)
                signal_path = analysis_dir / f"video_{video_id}_signals.json"
                signal_path.write_text(json.dumps(signal_json, ensure_ascii=False, indent=2), encoding="utf-8")
                
                proposal_md = generate_proposal_markdown(video_meta, analysis)
                proposal_path = proposals_dir / f"proposal_{video_id}.md"
                proposal_path.write_text(proposal_md, encoding="utf-8")
                
                # [NEW] Run Deep Logic Analysis & Save
                deep_result = deep_analyzer.analyze(
                    video_id=video_id,
                    title=video_meta.get("title", "Unknown"),
                    transcript=load_transcript(transcript_file)
                )
                deep_analyzer.save_report(deep_result, deep_dir)
                
                proposal_count += 1
                print(f"[Phase 31-B] Analyzed: {video_meta.get('title', video_id)}")
                
            except Exception as e:
                print(f"[Phase 31-B] Error processing {transcript_file.name}: {e}")
                continue
    
    return proposal_count


def main():
    base_dir = Path(__file__).parent.parent.parent
    print("[Phase 31-B] Starting Dynamic Narrative Analyzer")
    try:
        count = process_all_transcripts(base_dir)
        print(f"[Phase 31-B] Complete: {count} proposals generated via Dynamic Documentation Parsing")
    except Exception as e:
        print(f"[Phase 31-B] Error: {e}")

if __name__ == "__main__":
    main()
