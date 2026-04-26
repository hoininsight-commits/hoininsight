# src/core/gemini_client.py

import json
import os
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 프로젝트 루트 .env 명시적 로드
_ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)

DEBUG_DIR = Path("data/debug")
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiClient:
    """Gemini API 클라이언트 (Hardened & Safety Relaxed)"""

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.model_name = "gemini-2.5-flash"

        if not self.api_key:
            print("⚠️ [GeminiClient] WARNING: GEMINI_API_KEY not found. AI features will be disabled.")
            self.client = None
            return

        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-genai 미설치\n"
                "pip install google-genai"
            )

        self.client = genai.Client(api_key=self.api_key)
        self.health_path = Path("data/monitoring/gemini_health.json")
        self.session_cost = 0.0 # [v17.2] 현재 세션 총 비용 (USD)
        self._init_health()

    def _init_health(self):
        """health 파일 초기화 및 스케마 보정 (v4.6)"""
        if not self.health_path.exists():
            self.health_path.parent.mkdir(parents=True, exist_ok=True)
            self.health_path.write_text(json.dumps({
                "status": "NORMAL",
                "total_calls": 0,
                "failures": 0,
                "fallback_ratio": 0.0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "last_updated": ""
            }, indent=2))
        else:
            # 기존 파일에 토큰 필드 없으면 추가
            try:
                h = json.loads(self.health_path.read_text())
                if "total_input_tokens" not in h:
                    h["total_input_tokens"] = 0
                    h["total_output_tokens"] = 0
                    self.health_path.write_text(json.dumps(h, indent=2))
            except: pass

    def call_text(self, prompt: str, max_tokens: int = 4000) -> str:
        """Alias for call() to satisfy existing verification scripts"""
        return self.call(prompt, max_tokens)

    def call(self, prompt: str, max_tokens: int = 4000, is_json: bool = False) -> str:
        """텍스트 생성 호출 (Safety relaxed)"""
        # 1. 오프라인 캐시 체크
        mock_path = DEBUG_DIR / "mock_response.txt"
        if mock_path.exists():
            print(f"  📂 [OFFLINE_MODE] Using mock response from {mock_path.name}")
            return mock_path.read_text(encoding='utf-8').strip()

        if not self.client:
            return ""
        
        # 안전 설정 완화
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        config = genai.types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=0.1 if is_json else 0.7,
            safety_settings=safety_settings
        )
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config
        )
        
        # [COST_TRACKING] 토큰 사용량 기록 (v4.6)
        usage = getattr(response, "usage_metadata", None)
        if usage:
            self._update_health(
                success=True, 
                in_t=getattr(usage, "prompt_token_count", 0), 
                out_t=getattr(usage, "candidates_token_count", 0),
                tier=getattr(self, "current_tier", 3) # 세션 내 현재 티어 추적 필요
            )
        
        # [CRITICAL] 비정상 종료(MAX_TOKENS 등) 감지 시 즉각 에러 처리 (지시서 #082)
        reason = response.candidates[0].finish_reason
        if str(reason) != "FinishReason.STOP" and str(reason) != "STOP":
            error_msg = f"❌ Gemini 비정상 종료 (Reason: {reason}). 데이터 파손 위험으로 인해 에러 처리합니다."
            print(f"  {error_msg}")
            raise Exception(error_msg)

        # text 파트 추출
        text_parts = [part.text for part in response.candidates[0].content.parts if part.text]
        result = "".join(text_parts).strip()
        
        # [DEBUG] 마지막 응답 캡처
        try:
            (DEBUG_DIR / "last_raw_response.txt").write_text(result, encoding='utf-8')
        except: pass
        
        return result

    def call_json(self, prompt: str, max_tokens: int = 8192) -> dict:
        import json, re
        try:
            # 기본 호출
            response = self.call(prompt, max_tokens, is_json=True)
            return self.parse_json_with_recovery(response)

        except Exception as e:
            # TIER 3 등에서 에러가 너무 많이 나면 로깅 레벨 조절 가능
            # print(f"  ❌ call_json error: {e}") 
            raise e # wrapper에서 처리하도록 던짐

    def parse_json_with_recovery(self, response: str) -> dict:
        """응답 문자열로부터 JSON(Dict/List)을 파싱하고 복구하는 전용 엔진"""
        import json, re
        if not response: return {}
        
        # 정규화: 제어 문자 제거
        response = response.strip().replace('\x00', '')

        # 방법 1: 표준 파싱 시도
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 방법 2: ```json ... ``` 블록 추출
        match = re.search(r'```(?:json)?\s*([\s\S]*?)(?:```|$)', response)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except: pass

        # 방법 3: 공격적 복구 (잘린 JSON 대응 - { 혹은 [ 로 시작)
        bracket_match = re.search(r'([\{\[])', response)
        if bracket_match:
            start_char = bracket_match.group(1)
            end_char = '}' if start_char == '{' else ']'
            raw_json = response[bracket_match.start():].strip()
            
            # 잘린 괄호 강제 보정
            for _ in range(15): 
                try:
                    return json.loads(raw_json)
                except:
                    if not raw_json.endswith(end_char):
                        raw_json += end_char
                    else:
                        # 마지막 콤마 제거 후 닫기 시도
                        raw_json = re.sub(rf',\s*\{re.escape(end_char)}$', end_char, raw_json)
                        raw_json += end_char
            
            # 추가 시도: 객체 필드가 잘린 경우 필드 자체를 제거
            try:
                cleaned = re.sub(rf',\s*"[^"]*"\s*:\s*[^"{re.escape(end_char)}]*$', '', raw_json.rstrip(end_char)) + end_char
                return json.loads(cleaned)
            except: pass

        print(f"  ⚠️ JSON Recovery Failed. Length: {len(response)}")
        return {}

    def _update_health(self, success=True, in_t=0, out_t=0, tier=3):
        """실시간 호출 및 비용 상태 업데이트 (v17.2 Cost Calculation)"""
        import json
        
        # 비용 계산 (Gemini 1.5 가격 정책 기준)
        # Tier 1/2 (Pro 예상): In $3.5/1M, Out $10.5/1M
        # Tier 3 (Flash 예상): In $0.075/1M, Out $0.3/1M
        if tier in [1, 2]:
            cost = (in_t * 3.5 / 1000000) + (out_t * 10.5 / 1000000)
        else:
            cost = (in_t * 0.075 / 1000000) + (out_t * 0.3 / 1000000)
            
        self.session_cost += cost

        try:
            h = json.loads(self.health_path.read_text())
            h["total_calls"] += 1
            if not success: h["failures"] += 1
            
            h["total_input_tokens"] += in_t
            h["total_output_tokens"] += out_t
            h["total_accumulated_cost"] = h.get("total_accumulated_cost", 0.0) + cost
            
            h["fallback_ratio"] = round(h["failures"] / h["total_calls"], 2)
            h["last_updated"] = datetime.now().isoformat()
            
            self.health_path.write_text(json.dumps(h, indent=2, ensure_ascii=False))
            
            # [v17.2] 세션 비용 파일 업데이트
            session_path = Path("data/monitoring/session_cost.json")
            s_cost = 0.0
            if session_path.exists():
                try: s_cost = json.loads(session_path.read_text()).get("session_cost", 0.0)
                except: pass
            session_path.write_text(json.dumps({"session_cost": s_cost + cost, "last_updated": datetime.now().isoformat()}))
            
        except: pass

    def call_json_controlled(self, prompt: str, agent: str = "UNKNOWN", tier: int = 3, max_tokens: int = 8192) -> dict:
        """Control Layer가 적용된 JSON 호출 (v1.0, TIER 대응)"""
        from src.llm.gemini_wrapper import call_gemini_with_control
        return call_gemini_with_control(self, prompt, agent, tier=tier, max_tokens=max_tokens)

    def call_controlled(self, prompt: str, agent: str = "UNKNOWN", max_tokens: int = 8192, tier: int = 1) -> str:
        """Control Layer가 적용된 텍스트 호출 - TIER별 재시도 및 백오프 적용 (v1.3)"""
        from src.llm.gemini_wrapper import log_gemini_usage
        import time

        # [TASK #093] TIER별 설정
        # TIER 1: 필수 (4회 재시도), TIER 2: 중요 (2회), TIER 3: 보조 (0회)
        tier_config = {
            1: {"max_retries": 6, "backoff": [5, 10, 20, 30, 45, 60]},
            2: {"max_retries": 3, "backoff": [5, 10, 20]},
            3: {"max_retries": 1, "backoff": [5]}
        }
        
        config = tier_config.get(tier, tier_config[3])
        max_retries = config["max_retries"]
        backoff = config["backoff"]

        for attempt in range(max_retries + 1):
            try:
                # [GEMINI CALL] 텍스트 호출
                self.current_tier = tier # [v17.2] 비용 추적용 티어 주입
                res = self.call(prompt, max_tokens=max_tokens)
                if not res: 
                    raise Exception("Empty Text Response")
                
                log_gemini_usage(agent, success=True, fallback_used=False, retry_count=attempt)
                return res

            except Exception as e:
                err_msg = str(e).lower()
                is_server_error = any(code in err_msg for code in ["503", "500", "unavailable", "overloaded"])
                
                if is_server_error and attempt < max_retries:
                    wait_time = backoff[attempt] if attempt < len(backoff) else backoff[-1]
                    print(f"  ⚠️ [TIER {tier}] 과부하 감지. {wait_time}초 후 재시도... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                
                # 최종 실패 시
                self._update_health(success=False)
                log_gemini_usage(agent, success=False, fallback_used=True, retry_count=attempt)
                if tier == 1: # TIER 1만 에러를 전파하여 중단시키거나 강제 폴백 유도
                    raise e
                return ""
