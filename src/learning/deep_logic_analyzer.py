
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils.knowledge_base import KnowledgeBase
from src.llm.gemini_client import GeminiClient

class DeepLogicAnalyzer:
    """
    Performs deep structural analysis on video transcripts (Phase 31-B Enhanced).
    
    Steps:
    1. Surface Topic Removal
    2. Engine-View Real Topic Redefinition
    3. Anomaly Level Determination (L1-L3)
    4. WHY_NOW Trigger Analysis
    5. Core Assumptions Identification
    6. Data Collection Needs (Evolution Proposal)
    7. Difficulty vs Topic Filter
    8. Content Nature Assessment (Leading vs Lagging)
    9. Final Engine Summary
    """
    
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.surface_stopwords = [
            "주식", "투자", "시장", "매수", "매도", "전망", "분석", "이슈", "뉴스", 
            "종목", "추천", "대박", "수익", "리스크", "돈", "자산", "경제"
        ]
        try:
            self.llm = GeminiClient()
        except:
            self.llm = None
            print("[DeepLogicAnalyzer] Warning: GeminiClient init failed. Falling back to heuristics.")
        
    def analyze(self, video_id: str, title: str, transcript: str) -> Dict[str, Any]:
        """Run the full deep analysis pipeline."""
        
        # 1. Surface Topic Removal & Real Topic Extraction
        real_topic_info = self._extract_real_topic(transcript)
        
        # 2. Anomaly Level
        anomaly_info = self._determine_anomaly_level(transcript, real_topic_info['topic'])
        
        # 3. Why Now
        why_now_info = self._analyze_why_now(transcript)
        
        # 4. Evolution Proposals (Data Collection Needs)
        proposals = self._generate_evolution_proposals(video_id, transcript, real_topic_info['topic'])
        
        # 5. Core Assumptions (Heuristic)
        assumptions = self._extract_core_assumptions(transcript)
        
        # 6. Construct Final Report Data
        
        # [NEW] Try LLM Analysis
        llm_report = None
        if self.llm:
            llm_report = self._generate_llm_analysis(transcript, title)
            if llm_report:
                llm_proposals = self._parse_llm_proposals(video_id, llm_report)
                proposals.extend(llm_proposals)
            
        result = {
            "video_id": video_id,
            "title": title,
            "analysis_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "surface_topics": self._find_surface_topics(transcript),
            "real_topic": real_topic_info['topic'],
            "real_topic_reasoning": real_topic_info['reasoning'],
            "anomaly_level": anomaly_info['level'],
            "anomaly_reasoning": anomaly_info['reasoning'],
            "why_now": why_now_info,
            "core_assumptions": assumptions,
            "evolution_proposals": proposals, 
            "content_nature": "Leading Indicator" if anomaly_info['level'] == "L3" else "Lagging/Result",
            "engine_conclusion": self._generate_conclusion(real_topic_info, anomaly_info, why_now_info, assumptions),
            "llm_report": llm_report # Store full LLM content if available
        }
        
        return result

    def _find_surface_topics(self, transcript: str) -> List[str]:
        found = []
        for word in self.surface_stopwords:
            if word in transcript:
                found.append(word)
        return list(set(found))[:5]

    def _extract_real_topic(self, transcript: str) -> Dict[str, str]:
        """
        Find the most specific technical term defined in KnowledgeBase or high-frequency proper noun.
        """
        # 1. Try to match specific Data Definitions (Priority 1)
        data_defs = self.kb.get_data_definitions()
        best_match = None
        max_count = 0
        
        for d in data_defs:
            name = d.get('name', '')
            if name and name in transcript:
                count = transcript.count(name)
                if count > max_count:
                    max_count = count
                    best_match = name
        
        if best_match:
            return {
                "topic": best_match,
                "reasoning": f"Data Master Definition Match: '{best_match}' (mentioned {max_count} times)"
            }

        # 2. Try to match KB Keywords (Priority 2)
        keywords = self.kb.get_keywords_for_extraction()
        for kw in keywords:
            if kw in transcript:
                count = transcript.count(kw)
                if count > max_count:
                    max_count = count
                    best_match = kw
        
        if best_match:
            return {
                "topic": best_match,
                "reasoning": f"KB Keyword Match: '{best_match}' (mentioned {max_count} times)"
            }
            
        # 3. Fallback: Extract high-freq proper noun or specific terms (Simple Heuristic for Korean)
        # Look for English acronyms or 2+ chars Korean nouns
        matches = re.findall(r'[A-Z]{2,}|[가-힣]{2,}(?=[ 조사으로 은는이가])', transcript)
        if matches:
            from collections import Counter
            common = Counter(matches).most_common(1)
            if common:
                best_match = common[0][0]
                return {
                    "topic": best_match,
                    "reasoning": f"Heuristic Extraction: High-frequency term '{best_match}'"
                }

        return {
            "topic": "Unknown Structural Shift",
            "reasoning": "No direct match in Data Master. Requires semantic extraction."
        }

    def _determine_anomaly_level(self, transcript: str, topic: str) -> Dict[str, str]:
        """
        L1: Price Change
        L2: Supply/Demand Imbalance
        L3: Structural/Pattern Change or Bottleneck
        """
        score = 0
        reasoning_parts = []
        
        # L3 Keywords (Structural)
        l3_keywords = ["구조", "병목", "패러다임", "독점", "강제", "필수", "불가능", "대체 불가", "기술 전환"]
        for kw in l3_keywords:
            if kw in transcript:
                score += 3
                reasoning_parts.append(f"L3 Keyword '{kw}' found")
                
        # L2 Keywords (Flow)
        l2_keywords = ["수급", "재고", "부족", "과잉", "지연", "납품"]
        for kw in l2_keywords:
            if kw in transcript:
                score += 2
                reasoning_parts.append(f"L2 Keyword '{kw}' found")

        if score >= 5: # Hybrid or Strong L3
            return {"level": "L3", "reasoning": "High structural impact detected. " + ", ".join(reasoning_parts[:3])}
        elif score >= 2:
            return {"level": "L2", "reasoning": "Supply/Demand imbalance signals. " + ", ".join(reasoning_parts[:3])}
        else:
            return {"level": "L1", "reasoning": "Mostly price/sentiment level signals."}

    def _analyze_why_now(self, transcript: str) -> Dict[str, str]:
        triggers = []
        trigger_keywords = ["발표", "공시", "출시", "양산", "계약", "통과", "승인", "시작"]
        
        sentences = re.split(r'[.!?]\s+', transcript)
        for s in sentences:
            for kw in trigger_keywords:
                if kw in s and ("오늘" in s or "최근" in s or "이번" in s):
                    triggers.append(s.strip())
                    break
                    
        trigger_type = "Structural-driven" if triggers else "State-driven (Price/News)"
        description = triggers[0] if triggers else "No explicit immediate trigger found, likely a trend analysis."
        
        return {
            "trigger_type": trigger_type,
            "description": description
        }

    def _generate_evolution_proposals(self, video_id: str, transcript: str, topic: str) -> List[Dict[str, Any]]:
        """
        If the topic is significant (L3) but data is missing, propose adding it.
        """
        proposals = []
        
        # Heuristic: If we detected an L3 topic, but we don't have a specific dataset for 'Process Yield' or 'Bottleneck' related to it?
        # For this version, we will check if specific "needs" are mentioned.
        
        need_keywords = ["데이터가 필요", "지표를 봐야", "확인해야", "추적해야"]
        sentences = re.split(r'[.!?]\s+', transcript)
        
        for s in sentences:
            for nk in need_keywords:
                if nk in s:
                    # Found a data need
                    proposals.append({
                        "id": f"EVO-{datetime.utcnow().strftime('%Y%m%d')}-{abs(hash(s)) % 100000:05d}",
                        "video_id": video_id,
                        "category": "DATA_ADD",
                        "detected_pattern": f"User explicit need: {nk}",
                        "condition": s.strip()[:100],
                        "status": "PROPOSED"
                    })
                    break
        return proposals

    def _parse_llm_proposals(self, video_id: str, llm_report: str) -> List[Dict[str, Any]]:
        """Extract proposals from LLM Markdown report (Section 6)."""
        proposals = []
        try:
            # Regex to find Section 6
            match = re.search(r"## 6️⃣.*?Engine Evolution Suggestion.*?(\n.*?)($|#)", llm_report, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                # Parse lines like * **Proposed Sensor**: ...
                sensor = "Unknown Sensor"
                reason = "No reason provided"
                
                s_match = re.search(r"\* \*\*Proposed Sensor\*\*: (.*)", content)
                if s_match: sensor = s_match.group(1).strip()
                
                r_match = re.search(r"\* \*\*Reason\*\*: (.*)", content)
                if r_match: reason = r_match.group(1).strip()
                
                proposals.append({
                    "id": f"EVO-LLM-{datetime.utcnow().strftime('%Y%m%d')}-{abs(hash(sensor)) % 100000:05d}",
                    "video_id": video_id,
                    "category": "DATA_ADD", # or LOGIC_UPDATE based on content
                    "detected_pattern": "LLM Engine Evolution Suggestion",
                    "condition": sensor, # Store sensor name as condition
                    "meaning": reason,
                    "status": "PROPOSED"
                })
        except Exception as e:
            print(f"Error parsing LLM proposals: {e}")
        return proposals

    def _extract_core_assumptions(self, transcript: str) -> List[str]:
        # Heuristic: Look for "Because", "Therefore" structures (Korean: 때문에, 따라서)
        assumptions = []
        sentences = re.split(r'[.!?]\s+', transcript)
        for s in sentences:
            if "때문에" in s or "전제" in s:
                assumptions.append(s.strip())
        return assumptions[:3]

    def _generate_conclusion(self, topic_info, anomaly_info, why_now_info, assumptions) -> str:
        conclusion = f"엔진은 '{topic_info['topic']}'와(과) 관련하여 {anomaly_info['level']} 수준의 이상징후를 감지했습니다."
        if assumptions:
            conclusion += f" 핵심 가정: {assumptions[0]}"
        else:
            conclusion += f" {why_now_info['description']}"
        
        return conclusion

    def save_report(self, result: Dict[str, Any], output_dir: Path):
        """Save JSON and Markdown reports, and also save proposals to the evolution queue."""
        output_dir.mkdir(parents=True, exist_ok=True)
        base_dir = Path(os.getcwd())
        
        # JSON (Consolidated per date)
        json_path = output_dir / "deep_analysis_results.json"
        existing_data = []
        if json_path.exists():
            try:
                existing_data = json.loads(json_path.read_text(encoding='utf-8'))
                if not isinstance(existing_data, list): existing_data = [existing_data]
            except:
                pass
        
        existing_data.append(result)
        # Deduplicate by video_id
        existing_data_map = {v['video_id']: v for v in existing_data}
        json_path.write_text(json.dumps(list(existing_data_map.values()), ensure_ascii=False, indent=2), encoding='utf-8')
        
        # Markdown (Per video)
        md_path = output_dir / f"video_{result['video_id']}_report.md"
        md_content = self._format_markdown(result)
        md_path.write_text(md_content, encoding='utf-8')

        # [CRITICAL] Save individual proposals to data/evolution/proposals for dashboard visibility
        evo_dir = base_dir / "data" / "evolution" / "proposals"
        evo_dir.mkdir(parents=True, exist_ok=True)
        
        for p in result.get('evolution_proposals', []):
            p_id = p['id']
            evo_file = evo_dir / f"{p_id}.json"
            
            # Format to match dashboard's expectations
            evo_data = {
                "id": p_id,
                "video_id": p.get('video_id', ''),
                "generated_at": datetime.utcnow().isoformat(),
                "category": p.get('category', 'DATA_ADD'),
                "status": "PROPOSED",
                "content": {
                    "condition": p.get('condition', ''),
                    "meaning": p.get('meaning', f"Pattern: {p.get('detected_pattern', 'Unknown')}")
                },
                "evidence": {
                    "quote": p.get('condition', ''),
                    "source": result['title']
                }
            }
            evo_file.write_text(json.dumps(evo_data, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f"[Evolution] Exported proposal {p_id} to collection queue.")
        
    def _generate_llm_analysis(self, transcript: str, title: str) -> Optional[str]:
        """
        Generates a deep analysis report using Gemini with the Full Canonical Hoin Engine Context.
        """
        # 1. Load System Instruction
        engine_root = Path("resources/hoin_engine/v1.11")
        
        sys_instr_path = engine_root / "01_INSTRUCTION" / "GEMINI_SYSTEM_INSTRUCTION.md"
        if sys_instr_path.exists():
            system_instruction = sys_instr_path.read_text(encoding="utf-8")
        else:
            print("[DeepLogicAnalyzer] Warning: System Instruction not found. Using default.")
            system_instruction = "You are HOIN ENGINE. Analyze based on logic."

        # 2. Load All Canonical Docs (Reference Context)
        context_docs = []
        if engine_root.exists():
            for md_file in engine_root.rglob("*.md"):
                # Skip the system instruction itself to avoid duplication
                if md_file.name == "GEMINI_SYSTEM_INSTRUCTION.md":
                    continue
                # Skip irrelevant files if any
                if md_file.name.startswith("."):
                    continue
                
                try:
                    content = md_file.read_text(encoding="utf-8")
                    doc_name = md_file.name
                    # Calculate relative path for better context
                    rel_path = md_file.relative_to(engine_root)
                    context_docs.append(f"--- DOCUMENT: {rel_path} ---\n{content}\n")
                except Exception as e:
                    print(f"Warning: Failed to read {md_file}: {e}")

        full_context = "\n".join(context_docs)

        # 3. Construct Final Prompt
        prompt = f"""
{system_instruction}

=== CANONICAL REFERENCE LIBRARY (ABSOLUTE TRUTH) ===
You must strictly adhere to the definitions and logic in the following documents.
Do not use outside logic.

{full_context}

====================================================

=== CURRENT TASK ===
Analyze the following video transcript according to the HOIN ENGINE logic defined above.

# Input Data
- **Title**: {title}
- **Transcript**:
{transcript[:25000]} (truncated if too long)

# Output Requirement
Follow the [OUTPUT FORMAT] defined in the System Instruction.
"""
        return self.llm.generate_content(prompt)

    def _format_markdown(self, res: Dict[str, Any]) -> str:
        # If LLM report exists, use it as the primary content
        if res.get('llm_report'):
            return res['llm_report']
            
        # Fallback to Heuristic Report
        return f"""
# 🕵️‍♀️ HOIN ENGINE Deep Logic Analysis

## 1️⃣ 겉주제 제거 (Surface Topic 제거)
영상의 표면 메시지 (Removed):
{chr(10).join([f"* {t}" for t in res['surface_topics']])}

## 2️⃣ 엔진 관점의 '진짜 주제' 재정의 (Engine-View Real Topic)
* **Real Topic**: {res['real_topic']}
* **Reframed**: {res['real_topic_reasoning']}

## 3️⃣ 이상징후 레벨 판정 (ANOMALY LEVEL)
* **Level**: {res['anomaly_level']}
* **Reasoning**: {res['anomaly_reasoning']}

## 4️⃣ WHY_NOW 트리거 판정
* **Type**: {res['why_now']['trigger_type']}
* **Trigger**: {res['why_now']['description']}

## 5️⃣ 핵심 가정 (Core Assumptions)
{chr(10).join([f"* {a}" for a in res['core_assumptions']])}

## 6️⃣ DATA_COLLECTION_MASTER 관점 (Evolution Proposals)
{chr(10).join([f"* [PROPOSAL] {p['condition']}" for p in res['evolution_proposals']]) if res['evolution_proposals'] else "* (No new data collection needs identified)"}

## 7️⃣ 엔진 최종 판정 요약
> {res['engine_conclusion']}
"""
