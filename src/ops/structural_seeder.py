import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class StructuralTopicSeeder:
    """
    Step 63: Structural Topic Seeds v1.0
    Generates 'Pre-Anomaly' structural topic seeds (Damage/Redefinition)
    based on deterministic rules from existing signals.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("StructuralTopicSeeder")
        self.ymd = datetime.now().strftime("%Y-%m-%d")
        
        # KEYWORD RULES (Hardcoded for v1.0 as per constraints)
        self.DAMAGE_KEYWORDS = [
            "split", "spin-off", "merger", "dilution", "rights offering", 
            "owner", "governance", "dispute", "litigation", "class action",
            "fraud", "accounting", "restatement", "embezzlement",
            "물적분할", "유상증자", "경영권", "소송", "횡령", "배임", "감자"
        ]
        self.REDEFINITION_KEYWORDS = [
            "pivot", "transform", "new standard", "mandate", "export", 
            "global", "adoption", "first time", "re-rating", "paradigm",
            "transition", "inflection", "supply chain",
            "표준", "전환", "도입", "수출", "세계 최초", "재평가", "패러다임"
        ]
        
    def _load_json(self, path: Path) -> Dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def _classify_seed(self, item: Dict) -> Dict:
        """Classify a single item into DAMAGE or REDEFINITION or None"""
        
        # 1. Extract searchable text
        text_blob = (
            item.get('signal_title_kr', '') + " " + 
            item.get('signal_title', '') + " " +
            item.get('title', '') + " " +
            " ".join(item.get('core_fact', [])) + " " +
            item.get('structural_frame', '') + " " +
            item.get('frame', '')
        ).lower()
        
        # 2. Check Redefinition (Priority: Logic > Keywords)
        # Specific Frame Check from Signal
        frame = item.get('frame', '').upper()
        if frame in ['SUPPLY_CHAIN_MANDATE', 'TECH_SHIFT', 'REGULATORY_SHIFT', 'NEW_MARKET']:
            return self._build_seed_obj(item, "STRUCTURAL_REDEFINITION")
            
        for kw in self.REDEFINITION_KEYWORDS:
            if kw in text_blob:
                return self._build_seed_obj(item, "STRUCTURAL_REDEFINITION", match_kw=kw)

        # 3. Check Damage
        if frame in ['GOVERNANCE_RISK', 'SHAREHOLDER_DILUTION']:
            return self._build_seed_obj(item, "STRUCTURAL_DAMAGE")

        for kw in self.DAMAGE_KEYWORDS:
            if kw in text_blob:
                return self._build_seed_obj(item, "STRUCTURAL_DAMAGE", match_kw=kw)
                
        # 4. Fallback for Verified HOIN Engine Signals
        if 'signal_id' in item:
            return self._build_seed_obj(item, "HOIN_ANOMALY", match_kw="거시/시장 이상징후")
                
        return None

    def _build_seed_obj(self, item: Dict, seed_type: str, match_kw: str = "") -> Dict:
        # Generate safe ID
        base_id = item.get('signal_id', item.get('topic_id', 'unknown'))
        seed_id = f"STRUCT_{self.ymd.replace('-','')}_{base_id[:8]}"
        
        # Context summary
        title = item.get('signal_title_kr', item.get('title', 'Untitled'))
        
        if seed_type == "STRUCTURAL_DAMAGE":
            summary = f"구조적 피해 패턴 감지: '{match_kw}' 키워드 또는 프레임 매칭. 주주 가치 훼손 가능성."
            why_now = "반복 가능한 손실 메커니즘이 식별되었습니다."
            misunderstanding = "단발성 악재가 아닌 구조적 디스카운트 요인입니다."
            driver = ["GOVERNANCE"]
            risk = "대주주 의사결정 철회 시 해소 가능."
        elif seed_type == "STRUCTURAL_REDEFINITION":
            summary = f"구조적 재정의 패턴 감지: '{match_kw}' 키워드 또는 프레임 매칭. 시장 인식 변화 구간."
            why_now = "기존 PER/PBR 프레임에서 벗어나는 트리거가 발생했습니다."
            misunderstanding = "단순 호재가 아닌 밸류에이션 리레이팅(Re-rating) 시그널입니다."
            driver = ["INDUSTRY", "POLICY"] # Default heuristics
            risk = "실제 숫자(매출/이익)로 증명되기까지 시차 존재."
        else:
            summary = f"매크로/시장 이상 징후 감지: '{match_kw}'. 파급력 검토 필요."
            why_now = "엔진에서 유의미한 통계적 이상치(Anomaly)가 실시간으로 관찰되었습니다."
            misunderstanding = "시장 컨센서스와 실제 데이터 간 단기적 또는 구조적 괴리가 발생했을 수 있습니다."
            driver = ["MACRO", "MARKET"]
            risk = "시장의 단발성 노이즈일 가능성 존재 및 정책 대응 시차 우려."

        return {
            "run_date": self.ymd,
            "topic_seed_id": seed_id,
            "seed_type": seed_type,
            "structure_summary": f"[{title}] {summary}",
            "why_now": why_now,
            "market_misunderstanding": misunderstanding,
            "structural_driver": driver,
            "risk_side": risk,
            "status": "STRUCTURAL_ONLY",
            "source_refs": [
                {"kind": "artifact", "path": "hoin_signal/topic_seeds", "id": base_id}
            ],
            "created_at": self.ymd
        }

    def run(self):
        self.logger.info("Running StructuralTopicSeeder...")
        
        # 1. Load Inputs
        hoin_signals = self._load_json(self.base_dir / "data/ops/hoin_signal_today.json").get('signals', [])
        
        # topic_seeds.json is a list at root
        topic_seeds_raw = self._load_json(self.base_dir / "data/ops/topic_seeds.json")
        topic_seeds = topic_seeds_raw if isinstance(topic_seeds_raw, list) else topic_seeds_raw.get('seeds', [])

        # [NEW] Bridge Engine 1 Macro Anomalies (topic_candidates.json) into the flow
        ymd_path = self.ymd.replace("-", "/")
        topic_candidates_path = self.base_dir / "data/topics/candidates" / ymd_path / "topic_candidates.json"
        candidates_data = self._load_json(topic_candidates_path)
        macro_candidates = candidates_data.get('candidates', []) if candidates_data else []
        
        # Convert macro candidates into a format the seeder understands
        for cand in macro_candidates:
            if cand.get("status") == "CANDIDATE_ALIVE" or cand.get("status") == "UNKNOWN":
                cand['signal_id'] = cand.get('candidate_id', cand.get('dataset_id', 'unknown'))
                # Handle titles wrapped in metadata or nested
                title = cand.get('dataset_id', 'Unknown Macro Signal')
                if 'candidate_id' in cand:
                    cand['signal_title_kr'] = f"거시경제 이상징후: {title}"
                hoin_signals.append(cand)
        
        # 2. Process
        output_seeds = []
        seen_summaries = set()
        
        # Combine inputs (Signals have priority)
        all_candidates = hoin_signals + topic_seeds
        
        for item in all_candidates:
            seed = self._classify_seed(item)
            if seed:
                # Dedup
                sig = seed['structure_summary']
                if sig not in seen_summaries:
                    output_seeds.append(seed)
                    seen_summaries.add(sig)
        
        # 3. Output JSON
        out_json_path = self.base_dir / "data/ops/structural_topic_seeds_today.json"
        out_data = {
            "run_date": self.ymd,
            "count": len(output_seeds),
            "seeds": output_seeds,
            "errors": []
        }
        out_json_path.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding='utf-8')
        
        # 4. Output Markdown
        out_md_path = self.base_dir / "data/ops/structural_topic_seeds_today.md"
        md_content = self._generate_markdown(output_seeds)
        out_md_path.write_text(md_content, encoding='utf-8')
        
        self.logger.info(f"Generated {len(output_seeds)} structural seeds.")
        
    def _generate_markdown(self, seeds: List[Dict]) -> str:
        damage_seeds = [s for s in seeds if s['seed_type'] == 'STRUCTURAL_DAMAGE']
        redef_seeds = [s for s in seeds if s['seed_type'] == 'STRUCTURAL_REDEFINITION']
        
        md = f"# STRUCTURAL TOPIC SEEDS (PRE-ENGINE) - {self.ymd}\n\n"
        
        md += "## 1) STRUCTURAL DAMAGE (방어)\n"
        if not damage_seeds:
            md += "- 감지된 패턴 없음\n"
        for s in damage_seeds:
            md += f"### {s['topic_seed_id']}\n"
            md += f"- **Summary**: {s['structure_summary']}\n"
            md += f"- **Why Now**: {s['why_now']}\n"
            md += f"- **Risk**: {s['risk_side']}\n\n"
            
        md += "\n## 2) STRUCTURAL REDEFINITION (공격)\n"
        if not redef_seeds:
            md += "- 감지된 패턴 없음\n"
        for s in redef_seeds:
            md += f"### {s['topic_seed_id']}\n"
            md += f"- **Summary**: {s['structure_summary']}\n"
            md += f"- **Why Now**: {s['why_now']}\n"
            md += f"- **Driver**: {', '.join(s['structural_driver'])}\n"
            md += f"- **Risk**: {s['risk_side']}\n\n"
            
        return md

if __name__ == "__main__":
    # Test Run
    base = Path(__file__).resolve().parent.parent.parent
    seeder = StructuralTopicSeeder(base)
    seeder.run()
