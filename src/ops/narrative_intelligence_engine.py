import json
import os
from datetime import datetime
import shutil

class NarrativeIntelligenceEngine:
    def __init__(self):
        self.radar_path = "docs/data/ops/economic_hunter_radar.json"
        self.prob_path = "docs/data/ops/topic_probability_ranking.json"
        self.regime_path = "docs/data/ops/regime_state.json"
        self.os_path = "docs/data/ops/investment_os_state.json"
        self.timing_path = "docs/data/ops/timing_state.json"
        self.mentionables_path = "docs/data/decision/mentionables.json"
        
        self.output_local_path = "data/decision/narrative_intelligence.json"
        self.output_docs_path = "docs/data/decision/narrative_intelligence.json"

    def load_json(self, path):
        if not os.path.exists(path):
            print(f"Warning: File not found: {path}")
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def run(self):
        print("[Narrative Intelligence] Starting Step 13...")
        
        # Load Inputs
        radar = self.load_json(self.radar_path)
        prob = self.load_json(self.prob_path)
        regime = self.load_json(self.regime_path)
        os_state = self.load_json(self.os_path)
        timing = self.load_json(self.timing_path)
        mentionables = self.load_json(self.mentionables_path)
        
        if not prob or "top_topic_probability" not in prob:
            print("Error: No Top-1 Topic found in probability data.")
            return

        top_topic = prob["top_topic_probability"]
        radar_signals = radar.get("radar_candidates", []) if radar else []
        
        # Find matching radar signal for deep context
        matched_radar = next((r for r in radar_signals if r["signal_id"] == top_topic.get("signal_id")), None)
        
        # Find matching mentionables
        matched_mentions = []
        if mentionables:
            # Try matching by title or topic_id if available
            # In mentionables.json, we have topic_id and title. 
            # Probability ranking top_topic has potential_topic and signal_id.
            for m in mentionables:
                if m.get("title") == top_topic.get("potential_topic"):
                    matched_mentions = m.get("mentionables", [])
                    break

        # Synthesis
        storyline = {
            "hook": self.generate_hook(top_topic),
            "market_problem": self.generate_market_problem(regime, os_state),
            "mechanism": self.generate_mechanism(top_topic, matched_radar, timing),
            "implication": self.generate_implication(top_topic, regime),
            "stocks": self.generate_stock_section(matched_mentions),
            "conclusion": self.generate_conclusion(top_topic)
        }
        
        structural_context = {
            "regime": regime.get("regime_summary", {}).get("one_liner", "N/A") if regime else "N/A",
            "investment_os": os_state.get("os_summary", {}).get("stance", "N/A") if os_state else "N/A",
            "timing": timing.get("timing_gear", {}).get("label", "N/A") if timing else "N/A"
        }
        
        result = {
            "generated_at": datetime.now().isoformat(),
            "topic": top_topic.get("potential_topic"),
            "storyline": storyline,
            "structural_context": structural_context,
            "supporting_signals": top_topic.get("supporting_factors", []),
            "confidence": f"{top_topic.get('probability_score', 0)}%"
        }
        
        # Save Local
        os.makedirs(os.path.dirname(self.output_local_path), exist_ok=True)
        with open(self.output_local_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        # Publish to Docs
        os.makedirs(os.path.dirname(self.output_docs_path), exist_ok=True)
        shutil.copy2(self.output_local_path, self.output_docs_path)
        
        print(f"[Narrative Intelligence] Success. Generated at {self.output_docs_path}")

    def generate_hook(self, topic):
        title = topic.get("potential_topic", "이 이슈")
        return f"지금 월가가 갑자기 '{title}' 하나에 집착하는 진짜 이유, 알고 있으셨나요?"

    def generate_market_problem(self, regime, os_state):
        regime_msg = regime.get("regime_summary", {}).get("one_liner", "시장이 불안정한 흐름") if regime else "시장 지표가 엇갈리는 상황"
        stance = os_state.get("os_summary", {}).get("stance", "관망세") if os_state else "중립적인 입장"
        return f"현재 시장은 {regime_msg}을 보이고 있으며, 운영 관점에서는 {stance}를 유지해야 하는 엄중한 시점입니다."

    def generate_mechanism(self, topic, radar, timing):
        factors = ", ".join(topic.get("supporting_factors", [])[:2])
        timing_label = timing.get("timing_gear", {}).get("label", "NORMAL") if timing else "NORMAL"
        why_now = radar.get("why_now", "데이터상 유의미한 변화") if radar else "데이터상 임계점 도달"
        
        return f"이 현상은 단순한 소음이 아닙니다. {factors}와 같은 신호들이 {timing_label} 구간에서 동시에 폭발한 결과입니다. 특히 {why_now}라는 점에 주목해야 합니다."

    def generate_implication(self, topic, regime):
        bias = regime.get("regime_summary", {}).get("structural_bias", "자산 가격의 변동성 확대") if regime else "자산 가격의 변동성 확대"
        return f"결국 이 변화는 단순 일회성이 아니라 {bias}로 이어지며, 향후 투자 흐름의 판도를 완전히 바꿀 임플리케이션을 가집니다."

    def generate_stock_section(self, mentions):
        if not mentions:
            return ["현재 직접 연결된 추출 종목 없음 (바스켓 대응 권장)"]
        return mentions

    def generate_conclusion(self, topic):
        return f"요약하자면, '{topic.get('potential_topic')}' 소식은 단순 뉴스가 아니라 거대한 구조적 변화의 서막입니다. 지금 바로 대응을 준비해야 합니다."

if __name__ == "__main__":
    engine = NarrativeIntelligenceEngine()
    engine.run()
