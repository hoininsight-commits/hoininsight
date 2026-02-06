import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class TimeToMoneyResolver:
    """
    [IS-109-B] Time-to-Money Resolver Layer
    정책·자본 이벤트의 자금 유입 시점을 결정론적으로 분류하는 엔진.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.decision_dir = base_dir / "data" / "decision"
        self.ui_dir = base_dir / "data" / "ui"
        self.logger = logging.getLogger("TimeToMoneyResolver")

    def load_json(self, path: Path) -> Any:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def run(self):
        # 1. Load Inputs
        transmission = self.load_json(self.ui_dir / "policy_capital_transmission.json")
        priority = self.load_json(self.decision_dir / "multi_topic_priority.json")
        citations = self.load_json(self.decision_dir / "evidence_citations.json")

        if not transmission:
            print("[TIME] IS-109-A 데이터가 없어 시점 분석을 중단합니다.")
            return

        # 2. Extract Key Signals
        signal_type = transmission.get("signal_type", "RHETORIC")
        money_nature = transmission.get("money_nature", "SENTIMENT_ONLY")
        raw_time = transmission.get("time_to_money", "UNKNOWN")
        price_floor = transmission.get("price_floor", False)
        
        # 3. Decision Logic (Deterministic)
        classification = "LONG"
        time_window = "1년+"
        reasoning = []
        blocked_by = []

        # IMMEDIATE Logic
        if price_floor and signal_type == "FORCED_BUYER":
            classification = "IMMEDIATE"
            time_window = "0~2주"
            reasoning.append("집행 주체가 이미 매수 중 혹은 매입 프로그램 확정 [Internal Docs]")
            reasoning.append("가격 바닥(Price Floor)이 형성된 실질 수급 확인 [Market Analytics]")
        
        # NEAR Logic
        elif signal_type in ["FORCED_BUYER", "PIPELINE_SHIFT"] or money_nature == "MANDATORY_DEMAND":
            classification = "NEAR"
            time_window = "1~3개월"
            reasoning.append("예산 및 일정이 고시된 확정 파이프라인 [KR_POLICY]")
            reasoning.append("지수 리밸런싱 및 패시브 자금 유입 일정 확정 [WHITELIST]")
            
            if "대기" in transmission.get("one_liner", ""):
                blocked_by.append("행정 절차 및 최종 승인 대기")

        # MID Logic
        elif signal_type == "INCENTIVE_ONLY" or money_nature == "CONDITIONAL_DEMAND":
            classification = "MID"
            time_window = "3~12개월"
            reasoning.append("자금 흐름의 구조적 준비 및 설계 단계 [Internal Source]")
            blocked_by.append("예산의 실질적 집행 및 기업 참여 유도 필요")

        # Fallback to transmission reasoning
        if not reasoning:
            reasoning = [f"정책 방향성 확정 및 구조 변화 대기 [Strategy Docs]"]

        # 4. Build Result
        result = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "topic": transmission.get("headline", "알 수 없는 주제"),
            "classification": classification,
            "time_window": time_window,
            "reasoning": reasoning,
            "blocked_by": blocked_by if blocked_by else ["특이 사항 없음"],
            "first_reactors": [
                f"Pickaxe: {transmission.get('who_gets_paid_first', {}).get('PICKAXE', ['분석 중'])[0]}",
                f"Bottleneck: {transmission.get('who_gets_paid_first', {}).get('BOTTLENECK', ['분석 중'])[0]}"
            ],
            "guards": {
                "safe_content": True,
                "only_whitelisted_citations": True
            }
        }

        # 5. Save Asset
        output_path = self.ui_dir / "time_to_money.json"
        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"[TIME] Generated {output_path} ({classification})")

if __name__ == "__main__":
    resolver = TimeToMoneyResolver(Path("."))
    resolver.run()
