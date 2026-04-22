import json
import os
from pathlib import Path
from datetime import datetime
from src.topic_engine.event_generator import EventGenerator
from src.topic_engine.data_generator import DataSignalGenerator
from src.topic_engine.hybrid_generator import HybridGenerator
from src.topic_engine.candidate_packer import CandidatePacker
from src.topic_engine.evaluator import TopicEvaluator
from src.topic_engine.selector import TopicSelector

class TopicSelectionEngine:
    """[TASK #100] 통합 토픽 선정 엔진"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.today = datetime.now().strftime("%Y%m%d")
        self.topic_dir = self.base_dir / "data/topics"
        self.topic_dir.mkdir(parents=True, exist_ok=True)
        
        self.event_gen = EventGenerator()
        self.data_gen = DataSignalGenerator()
        self.hybrid_gen = HybridGenerator()
        self.packer = CandidatePacker()
        self.evaluator = TopicEvaluator()
        self.selector = TopicSelector()

    def run(self, raw_data: dict):
        print(f"🚀 Topic Selection Engine v10.0 가동")
        
        # 1. 데이터 추출
        news_headlines = raw_data.get("sentiment", {}).get("data", {}).get("news_headlines", [])
        market_data = raw_data.get("market", {})
        
        # 2. 후보 생성 (Deterministic)
        events = self.event_gen.generate(news_headlines)
        signals = self.data_gen.generate(market_data)
        hybrids = self.hybrid_gen.generate(events, signals)
        
        # 3. 패키징
        candidates = self.packer.pack_all(events, signals, hybrids)
        self._save_json(candidates, "topic_candidates.json")
        print(f"  ✅ Candidates Generated: {len(candidates)}")
        
        # 4. LLM 평가
        evaluations = self.evaluator.evaluate_all(candidates)
        self._save_json(evaluations, "topic_evaluations.json")
        print(f"  ✅ Evaluations Completed: {len(evaluations)}")
        
        # 5. 최종 선정
        selection = self.selector.select(candidates, evaluations)
        self._save_json(selection, "topic_selection.json")
        
        if selection["MAIN"]:
            print(f"  🏆 MAIN Topic: {selection['MAIN']['title_seed']}")
            
        return selection

    def _save_json(self, data, filename):
        path = self.topic_dir / filename
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
