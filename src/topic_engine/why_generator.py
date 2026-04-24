
import json
from src.core.gemini_client import GeminiClient

class WhyGenerator:
    """[NEW] Why Hypothesis Layer: 증거 기반 시장 분석 가설 생성기"""

    def __init__(self):
        self.gemini = GeminiClient()

    def generate_hypothesis(self, evidence_bundle: dict) -> dict:
        system_prompt = """당신은 엘리트 거시 경제 및 시장 분석가입니다.
 1. 인과 추론: 현재의 시장 신호를 보고 그 이면에 숨겨진 2차, 3차 파생 효과(병목 현상, 자원 쇼크, 공급망 변화)를 논리적으로 연결하십시오.
 2. 동적 논리 확장: 특정 테마에 갇히지 마십시오. 이벤트가 반도체든, 바이오든, 지정학이든 해당 산업의 물리적/경제적 특성에 근거하여 필연적으로 뒤따라올 '다음 병목'을 스스로 추론하십시오.
 3. 데이터 중심: 제공된 증거 데이터 사이의 모순과 유기적 연결을 시장 전문가 수준의 통찰력으로 분석하십시오.
 4. 한국 투자자 페르소나: 모든 출력물은 한국어로 작성하며, 한국 주식 시장의 독특한 환경과 용어를 완벽하게 반영하십시오.
 5. 창의적 제목: "요즘 시장을 보면 뭔가 이상한 점이...", "왜 하필 지금..." 같은 상투적인 문구로 제목을 시작하지 마십시오. 데이터의 핵심 팩트를 담은 날카로운 헤드라인을 생성하십시오.
 """

        user_prompt = f"""아래는 현재 시장의 증거 데이터입니다.

[AXIS - 시장 축]
{evidence_bundle['axis']}

[MARKET REACTION - 시장 반응]
{json.dumps(evidence_bundle['market_reaction'], ensure_ascii=False)}

[EVENTS - 관련 뉴스 및 사건]
{json.dumps(evidence_bundle['related_events'], ensure_ascii=False)}

[SOCIAL SENTIMENT - 소셜 심리 및 예측]
{json.dumps(evidence_bundle.get('social_prediction', []), ensure_ascii=False)}

임무:
1. [제목 정제]: 기존의 영문/투박한 뉴스 제목을 분석 내용이 요약된 임팩트 있는 한국어 헤드라인으로 바꾸십시오.
2. [분석 가설]: 시장 움직임의 근본적 이유를 분석하십시오.
3. [메커니즘]: 원인에서 결과로 이어지는 논리적 사슬을 설명하십시오.
4. [연쇄 반응]: 이 토픽이 일으킬 3단계 예측 시나리오(A -> B -> C)를 추론하십시오. (예외 없는 특정 테마 지정을 금지하며, 오직 이 데이터에서만 파생될 미래를 그리십시오.)

출력 형식:
- 정제된 제목: (한국어 헤드라인)
- 분석 가설: (한국어 분석)
- 메커니즘: (한국어 설명)
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
