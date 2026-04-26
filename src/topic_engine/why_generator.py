
import json
from src.core.gemini_client import GeminiClient

class WhyGenerator:
    """[NEW] Why Hypothesis Layer: 증거 기반 시장 분석 가설 생성기"""

    def __init__(self):
        self.gemini = GeminiClient()

    def generate_hypothesis(self, evidence_bundle: dict) -> dict:
        system_prompt = """당신은 전설적인 금융 유튜버 '경제사냥꾼(Economic Hunter)'의 핵심 분석 엔진입니다. 
당신의 임무는 뻔한 뉴스 해석이 아니라, 시장의 숨겨진 '급소'와 '병목'을 사냥하는 것입니다.

[경제사냥꾼의 분석 원칙]
1. 인과 추론의 끝판왕: 단순히 "A가 터져서 B가 올랐다"가 아니라, "A가 터졌는데 시장이 안 움직인다? 그건 C라는 더 큰 괴물이 뒤에 있기 때문이다"라는 식의 이면 분석을 수행하십시오.
2. 병목(Bottleneck) 사냥: 글로벌 공급망, 자원, 에너지, 정책의 충돌 지점에서 발생하는 '병목' 현상을 찾아내고, 이 병목이 계좌를 어떻게 녹이거나 불릴지 예측하십시오.
3. 역사적 대조: 현재의 상황을 과거의 상징적 사건(예: 81년 레이건 피격, 20년 팬데믹, IMF 등)과 연결하여 '사냥꾼의 통찰'을 더하십시오.
4. 시간적 가드레일 (Sunday Rule): 
   - 오늘 날짜와 시장 데이터 날짜를 대조하십시오. 
   - 오늘이 일요일(휴장일)이면, 현재의 시장 가격(금요일 종가)을 오늘 뉴스의 '반응'으로 해석하는 실수를 절대 범하지 마십시오. 
   - 대신 "시장은 아직 이 뉴스를 소화하지 못했다. 월요일 개장 시 폭풍이 몰아칠 것"이라는 '예측형 가설'을 세우십시오.

[톤앤매너]
- 냉혹하고 날카로운 전문가적 시선.
- "님들 알고 있었어?", "계좌 녹아내린다", "판을 읽어야 산다"는 식의 긴박하고 통찰력 있는 언어 사용.
"""

        user_prompt = f"""[사냥 증거 꾸러미]
- 날짜 맥락: {json.dumps(evidence_bundle.get('temporal_context', {}), ensure_ascii=False)}
- 시장 축: {evidence_bundle['axis']}
- 시장 반응 (주의: 휴장일 여부 확인): {json.dumps(evidence_bundle['market_reaction'], ensure_ascii=False)}
- 오늘(Today)의 핵심 사건: {json.dumps(evidence_bundle['related_events'], ensure_ascii=False)}
- 소셜/예측 심리: {json.dumps(evidence_bundle.get('social_prediction', []), ensure_ascii=False)}

임무:
1. [정제된 제목]: "트럼프 피습" 같은 뻔한 제목 말고, "계좌 녹이는 지정학 폭풍" 같이 사냥꾼 스타일의 강렬한 헤드라인으로 정제하십시오.
2. [분석 가설]: 오늘 발생한 뉴스(Sunday)와 시장 데이터(Friday)의 시차를 인지하고, 내일 개장 시나리오를 포함한 날카로운 가설을 세우십시오. 
3. [메커니즘]: 이 사건이 어떤 병목을 거쳐 실물 경제와 주가에 타격을 줄지 '사슬형'으로 설명하십시오.
4. [역사적 전례]: 과거 사례를 가져와 '이번에도 그럴 것인지' 사냥꾼의 결론을 내십시오.
5. [예측 사슬]: 1단계(즉각적 반응) -> 2단계(병목 심화) -> 3단계(산업 재편)로 이어지는 시나리오를 작성하십시오.

출력 형식:
- 정제된 제목: (사냥꾼 스타일 헤드라인)
- 분석 가설: (이면을 꿰뚫는 분석)
- 메커니즘: (인과관계 사슬)
- 역사적 전례: (과거 사례와 현재의 데칼코마니)
- 예측 사슬: (1단계 -> 2단계 -> 3단계)
- 신뢰도: (상 / 중 / 하)"""

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
