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
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def _ymd() -> str:
    """Get current UTC date in YYYY/MM/DD format."""
    return datetime.utcnow().strftime("%Y/%m/%d")


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


def extract_topic_candidates(transcript: str) -> List[Dict[str, Any]]:
    """
    Extract topic candidates from transcript.
    
    Strategy:
    - Identify repeated economic/market keywords
    - Extract surrounding context as evidence
    - NO interpretation, just extraction
    """
    # Economic/market keywords to look for
    keywords = [
        "환율", "금리", "달러", "원화", "위안화",
        "주식", "지수", "코스피", "나스닥", "S&P",
        "부동산", "아파트", "집값",
        "인플레이션", "물가", "CPI",
        "실업", "고용", "일자리",
        "GDP", "성장률", "경기",
        "채권", "국채", "회사채",
        "원자재", "금", "은", "구리", "원유",
        "반도체", "배터리", "전기차",
        "중국", "미국", "일본", "유럽",
        "연준", "Fed", "한국은행", "중앙은행"
    ]
    
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
    
    return candidates[:5]  # Top 5 candidates


def extract_why_now_clues_from_sentences(sentences: List[str]) -> List[str]:
    """Extract WHY NOW temporal markers and triggers from sentences."""
    clues = []
    
    # Temporal markers
    temporal_markers = [
        "지금", "최근", "이번 달", "이번 주", "오늘", "곧",
        "최근 데이터", "최신", "현재", "당장", "바로 지금"
    ]
    
    # Trigger words
    trigger_words = [
        "급등", "급락", "폭등", "폭락", "급격히", "갑자기",
        "처음으로", "사상 처음", "역대", "최고", "최저",
        "돌파", "붕괴", "임계", "전환", "변곡",
        "발표", "정책", "결정", "조치", "개입"
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


def suggest_engine_mapping_hints(candidates: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Suggest potential DATA_COLLECTION_MASTER axes and ANOMALY_DETECTION_LOGIC triggers.
    
    IMPORTANT: These are SUGGESTIONS only, NOT applied automatically.
    """
    data_axes = set()
    anomaly_triggers = set()
    
    # Mapping keywords to data axes (suggestion only)
    axis_mapping = {
        "환율": "FX_RATES",
        "달러": "FX_RATES",
        "원화": "FX_RATES",
        "금리": "INTEREST_RATES",
        "채권": "BOND_YIELDS",
        "국채": "BOND_YIELDS",
        "주식": "EQUITY_INDEX",
        "지수": "EQUITY_INDEX",
        "코스피": "EQUITY_INDEX",
        "나스닥": "EQUITY_INDEX",
        "S&P": "EQUITY_INDEX",
        "금": "COMMODITIES",
        "원유": "COMMODITIES",
        "원자재": "COMMODITIES",
        "인플레이션": "INFLATION",
        "물가": "INFLATION",
        "CPI": "INFLATION",
        "GDP": "MACRO_INDICATORS",
        "성장률": "MACRO_INDICATORS",
        "실업": "EMPLOYMENT",
        "고용": "EMPLOYMENT"
    }
    
    # Mapping WHY NOW clues to anomaly triggers (suggestion only)
    trigger_mapping = {
        "급등": "Rapid price surge",
        "급락": "Rapid price drop",
        "돌파": "Threshold breakout",
        "처음으로": "Historical first",
        "최고": "All-time high",
        "최저": "All-time low",
        "정책": "Policy announcement",
        "발표": "Data release"
    }
    
    for candidate in candidates:
        topic = candidate.get("topic", "")
        
        # Suggest data axes
        for keyword, axis in axis_mapping.items():
            if keyword in topic:
                data_axes.add(axis)
        
        # Suggest anomaly triggers
        for clue in candidate.get("why_now_clues", []):
            for keyword, trigger in trigger_mapping.items():
                if keyword in clue:
                    anomaly_triggers.add(trigger)
    
    return {
        "data_axes": sorted(list(data_axes)),
        "anomaly_triggers": sorted(list(anomaly_triggers))
    }


def analyze_transcript(transcript_path: Path, video_meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main analysis function: extract topic candidates and WHY NOW signals.
    
    Returns analysis dict with:
    - topic_candidates: List of extracted topics
    - engine_mapping_hints: Suggested axes and triggers
    """
    transcript = load_transcript(transcript_path)
    
    if not transcript:
        return {
            "topic_candidates": [],
            "engine_mapping_hints": {"data_axes": [], "anomaly_triggers": []}
        }
    
    # Extract topic candidates
    candidates = extract_topic_candidates(transcript)
    
    # Generate engine mapping hints (suggestions only)
    hints = suggest_engine_mapping_hints(candidates)
    
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
        "note": "This file is for proposal review only. No automatic engine update."
    }


def generate_proposal_markdown(video_meta: Dict[str, Any], analysis: Dict[str, Any]) -> str:
    """Generate proposal markdown output."""
    lines = []
    
    lines.append("# Narrative Proposal (Review Required)")
    lines.append("")
    lines.append("## Source")
    lines.append(f"- Video: {video_meta.get('title', 'Unknown')}")
    lines.append(f"- URL: https://www.youtube.com/watch?v={video_meta.get('video_id', '')}")
    lines.append(f"- Published at: {video_meta.get('published_at', 'Unknown')}")
    lines.append("")
    
    lines.append("## Topic Candidates")
    candidates = analysis.get("topic_candidates", [])
    if candidates:
        for candidate in candidates:
            lines.append(f"- {candidate.get('topic', 'Unknown')}")
    else:
        lines.append("- (No candidates extracted)")
    lines.append("")
    
    lines.append("## WHY NOW Signals (Extracted)")
    why_now_found = False
    for candidate in candidates:
        for clue in candidate.get("why_now_clues", []):
            lines.append(f"- {clue}")
            why_now_found = True
    if not why_now_found:
        lines.append("- (No WHY NOW signals detected)")
    lines.append("")
    
    lines.append("## Engine Extension Suggestions (NOT APPLIED)")
    hints = analysis.get("engine_mapping_hints", {})
    
    lines.append("### Data Collection")
    data_axes = hints.get("data_axes", [])
    if data_axes:
        for axis in data_axes:
            lines.append(f"- {axis}")
    else:
        lines.append("- (No suggestions)")
    lines.append("")
    
    lines.append("### Anomaly Detection")
    triggers = hints.get("anomaly_triggers", [])
    if triggers:
        for trigger in triggers:
            lines.append(f"- {trigger}")
    else:
        lines.append("- (No suggestions)")
    lines.append("")
    
    lines.append("## Safety Notice")
    lines.append("This proposal is automatically generated.")
    lines.append("No engine logic, data schema, or definitions have been modified.")
    lines.append("Manual review and explicit approval are required for any additive changes.")
    
    return "\n".join(lines)


def process_all_transcripts(base_dir: Path) -> int:
    """
    Process all transcripts from today's collection.
    
    Returns count of proposals generated.
    """
    ymd = _ymd()
    transcripts_dir = base_dir / "data" / "narratives" / "transcripts" / ymd.replace("/", "/")
    
    if not transcripts_dir.exists():
        print(f"[Phase 31-B] No transcripts found for {ymd}")
        return 0
    
    # Create output directories
    analysis_dir = base_dir / "data" / "narratives" / "analysis" / ymd.replace("/", "/")
    proposals_dir = base_dir / "data" / "narratives" / "proposals" / ymd.replace("/", "/")
    analysis_dir.mkdir(parents=True, exist_ok=True)
    proposals_dir.mkdir(parents=True, exist_ok=True)
    
    proposal_count = 0
    
    # Process each transcript
    for transcript_file in transcripts_dir.glob("*.txt"):
        try:
            video_id = transcript_file.stem
            
            # Find corresponding video metadata
            raw_dir = base_dir / "data" / "narratives" / "raw" / "youtube"
            video_meta = None
            
            for video_dir in raw_dir.rglob("*"):
                if video_dir.is_dir():
                    meta = load_video_metadata(video_dir)
                    if meta and meta.get("video_id") == video_id:
                        video_meta = meta
                        break
            
            if not video_meta:
                print(f"[Phase 31-B] Warning: No metadata found for {video_id}, skipping")
                continue
            
            # Analyze transcript
            analysis = analyze_transcript(transcript_file, video_meta)
            
            # Generate signal JSON
            signal_json = generate_signal_json(video_meta, analysis)
            signal_path = analysis_dir / f"video_{video_id}_signals.json"
            signal_path.write_text(json.dumps(signal_json, ensure_ascii=False, indent=2), encoding="utf-8")
            
            # Generate proposal markdown
            proposal_md = generate_proposal_markdown(video_meta, analysis)
            proposal_path = proposals_dir / f"proposal_{video_id}.md"
            proposal_path.write_text(proposal_md, encoding="utf-8")
            
            proposal_count += 1
            print(f"[Phase 31-B] Generated proposal for: {video_meta.get('title', video_id)}")
            
        except Exception as e:
            print(f"[Phase 31-B] Error processing {transcript_file.name}: {e}")
            continue
    
    return proposal_count


def main():
    """Main entry point for Phase 31-B."""
    base_dir = Path(__file__).parent.parent.parent
    
    print("[Phase 31-B] Starting Narrative Analyzer")
    print("[Phase 31-B] SAFETY: Proposal-only mode, no engine modifications")
    
    try:
        count = process_all_transcripts(base_dir)
        print(f"[Phase 31-B] Complete: {count} proposals generated")
    except Exception as e:
        print(f"[Phase 31-B] Error: {e}")
        # Soft-fail: don't raise exception to avoid breaking pipeline


if __name__ == "__main__":
    main()
