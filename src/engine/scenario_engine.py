
import json
from pathlib import Path

class ScenarioEngine:
    """[TASK #089] SCENARIO ENGINE
    각 신호/이벤트에 대해 '가능한 모든 합리적 시나리오' 생성
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        from src.core.gemini_client import GeminiClient
        self.gemini = GeminiClient()
        
    def generate_scenarios(self, candidates: list, interpretations: list) -> list:
        all_scenarios = []
        
        # Link interpretations to candidates for context
        for cand in candidates:
            topic = cand["topic"]
            # Find related interpretation
            interp = next((i for i in interpretations if i["event"] in topic), None)
            
            scenarios = self._generate_scenario_set(cand, interp)
            
            all_scenarios.append({
                "topic": topic,
                "scenarios": scenarios
            })
            
        # 결과 저장
        save_path = self.output_dir / "scenarios_today.json"
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(all_scenarios, f, ensure_ascii=False, indent=2)
            
        return all_scenarios

    def _generate_scenario_set(self, candidate: dict, interpretation: dict) -> list:
        """지표와 상황에 맞는 시나리오 3개 생성"""
        # [PROMPT for Scenario Generation]
        # 이 컴포넌트는 새로운 기능이므로 내부 프롬프트를 정의합니다.
        
        prompt = f"""
        당신은 금융 시장 분석가입니다. 다음 '이상징후 토픽'과 '시장 흐름'을 분석하여, 
        현재 상황을 설명할 수 있는 **상반된 3가지 합리적 시나리오**를 제시하세요.
        
        [토픽] {candidate['topic']}
        [해석 요약] {json.dumps(interpretation['normal_flow'] if interpretation else {}, ensure_ascii=False)}
        
        [요구사항]
        1. 각 시나리오는 정밀한 검증 지표(Validation Targets)를 포함해야 합니다.
        2. '정상 흐름', '일시적 왜곡', '새로운 추세 형성' 등 다양한 관점을 유지하세요.
        3. 반드시 아래 JSON 형식으로 응답하세요.
        
        [응답 형식]
        [
          {{
            "scenario": "시나리오 제목",
            "explanation": "시나리오 상세 설명",
            "validation_targets": ["추적 지표1 방향", "추적 지표2 방향"]
          }}
        ]
        """
        try:
            res = self.gemini.call_json_controlled(prompt, agent="DETECTOR")
            if res and isinstance(res, list) and len(res) >= 3:
                return res
        except:
            pass

        # Fallback (Manual scenarios if Gemini fails)
        return [
            {"scenario": "시장 선반영", "explanation": "뉴스가 나오기 전 이미 가격이 움직여 반대 방향으로 되돌림", "validation_targets": ["거래량 감소", "이익실현 매물"]},
            {"scenario": "매크로 노이즈", "explanation": "지정학 이슈보다 더 큰 매크로 지표(금리/환율)가 시장을 압도", "validation_targets": ["USD_KRW 상승", "국채금리 급등"]},
            {"scenario": "수급 불균형", "explanation": "특정 수급 주체(외인/기관)의 강제 포지션 청산으로 인한 비이성적 흐름", "validation_targets": ["외인 순매도 지속", "선물 미결제 약정 변화"]}
        ]
