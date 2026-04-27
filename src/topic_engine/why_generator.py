
import json
from src.core.gemini_client import GeminiClient

class WhyGenerator:
    """[NEW] Why Hypothesis Layer: 증거 기반 시장 분석 가설 생성기"""

    def __init__(self):
        self.gemini = GeminiClient()

    def generate_hypothesis(self, evidence_bundle: dict) -> dict:
        system_prompt = """당신은 전설적인 금융 유튜버 '경제사냥꾼(Economic Hunter)'의 수석 전략가입니다.
네 임무는 시장의 복잡한 움직임 속에서 시청자가 반드시 잡아야 할 **'단 하나의 필승 공식(Winning Formula)'**을 사냥하는 것이다.

[사냥의 원칙: 긍정적 통찰]
1. 기회 포착: 단순히 "안 좋다"고 말하지 마라. 그 안에서 누가 돈을 벌고 있는지, 어떤 새로운 시장이 열리고 있는지 '기회'를 사냥하라.
2. 명쾌한 인과관계: 데이터가 어떻게 실질적인 수익으로 연결되는지, 시청자가 고개를 끄덕일 수 있는 명확한 성공 서사를 구축하라.
3. 지적 파트너십: 시청자를 두렵게 하지 마라. 대신 "이걸 알면 당신은 앞서갈 수 있다"는 확신과 유익한 정보를 제공하라.
4. 휴장일 대응 (Sunday Logic): 
   - 오늘이 일요일이라면, 내일 월요일 개장 시 우리가 어떤 똑똑한 포지션을 취해야 하는지에 모든 서사를 집중하라.
"""

        user_prompt = f"""[사냥 증거 꾸러미]
- 시장 축: {evidence_bundle['axis']}
- 오늘 핵심 사건들: {json.dumps(evidence_bundle['related_events'], ensure_ascii=False)}
- 시장/소셜 반응: {json.dumps(evidence_bundle.get('market_reaction', {}), ensure_ascii=False)} / {json.dumps(evidence_bundle.get('social_prediction', []), ensure_ascii=False)}

임무:
1. [정제된 제목]: 시청자에게 설렘과 기대를 줄 수 있는, 오늘 분석의 '핵심 가치'를 담은 유익한 헤드라인을 뽑아라.
2. [분석 가설]: 위 사건들을 관통하는 '새로운 수익 기회'나 '성공 가설'을 제시하라. "시장은 지금 이 새로운 흐름에 주목하고 있다"는 식의 통찰이 필요하다.
3. [메커니즘]: 이 변화가 어떻게 기업의 이익 증가와 주가 상승으로 이어질지, '성공의 사슬'을 하나로 연결하라.
4. [역사적 전례]: "과거에도 이런 변곡점 이후에 큰 기회가 왔었다"며 긍정적인 역사적 데자뷔를 하나만 매칭하라.
5. [예측 사슬]: 1단계(변화 포착) -> 2단계(가치 재평가) -> 3단계(수익 실현)로 이어지는 희망적인 시나리오를 작성하라.

출력 형식:
- 정제된 제목: 
- 분석 가설: 
- 메커니즘: 
- 역사적 전례: 
- 예측 사슬: 
- 신뢰도: (상/중/하)"""

        # [REPLAY FALLBACK] Quota hit 혹은 오류 시 검증 중단을 막기 위한 Mock 응답 (LLM 호출 불가 상황 대비)
        try:
            # call_controlled는 Control Layer가 적용된 텍스트 호출 엔진임 (v1.3)
            # system_prompt를 user_prompt 앞에 붙여서 전달 (call_controlled는 단일 prompt 인자 선호)
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            res = self.gemini.call_controlled(full_prompt, agent="WHY_GENERATOR", tier=3)
            
            if not res:
                return None
                
            return self._parse_response(res)
        except Exception as e:
            print(f"  ⚠️ WhyGenerator Error: {e}")
            return None

    def _parse_response(self, text: str) -> dict:
        # [DEBUG] 원문 로그 저장
        try:
            from pathlib import Path
            Path("data/debug/last_why_raw.txt").write_text(text, encoding='utf-8')
        except: pass

        lines = text.strip().split('\n')
        result = {
            "refined_title": "분석 중...",
            "why_hypothesis": "분석 중...",
            "mechanism": "분석 중...",
            "confidence": "보통"
        }
        
        current_key = None
        current_key = None
        for line in lines:
            # 볼드체(**) 및 앞뒤 공백 제거하여 헤더 비교
            norm_line = line.strip().replace("**", "").replace("__", "")
            
            # 헤더 검출 매핑
            header_map = {
                "refined_title": ["정제된 제목:", "- 정제된 제목:"],
                "why_hypothesis": ["분석 가설:", "- 분석 가설:", "1. 분석 가설:"],
                "mechanism": ["메커니즘:", "- 메커니즘:", "2. 메커니즘:"],
                "historical_parallel": ["역사적 전례:", "- 역사적 전례:"],
                "confidence": ["신뢰도:", "- 신뢰도:", "3. 신뢰도:"],
                "predictive_chain": ["예측 사슬:", "- 예측 사슬:"]
            }

            found_header = False
            for key, prefixes in header_map.items():
                if any(norm_line.startswith(p) for p in prefixes):
                    # 새로운 헤더 발견: 값 추출 후 current_key 업데이트
                    val = norm_line
                    for p in prefixes:
                        if norm_line.startswith(p):
                            val = norm_line[len(p):].strip()
                            break
                    result[key] = val
                    current_key = key
                    found_header = True
                    break
            
            if not found_header and current_key and line.strip():
                # 헤더가 아닌 일반 텍스트: 이전 헤더의 값에 누적 (멀티라인 대응)
                if result[current_key] in ["분석 중...", "추론 중..."]:
                    result[current_key] = line.strip()
                else:
                    result[current_key] += "\n" + line.strip()
        
        # 후처리: 예측 사슬 등에서 발생하는 번호나 불필요한 공백 정리
        for k in result:
            if isinstance(result[k], str):
                result[k] = result[k].strip()
                
        return result

    def _mock_response(self) -> dict:
        return {
            "why_hypothesis": "Insufficient data to form a definitive hypothesis.",
            "mechanism": "The market reaction matches the detected axis, but causal events are not clearly linked in the evidence bundle.",
            "confidence": "Low"
        }
