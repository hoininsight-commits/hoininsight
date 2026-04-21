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
        self.model_name = "gemini-flash-latest"

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
                out_t=getattr(usage, "candidates_token_count", 0)
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
            print(f"  ❌ call_json error: {e}")
            return {}

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

    def _update_health(self, success=True, in_t=0, out_t=0):
        """실시간 호출 및 비용 상태 업데이트"""
        import json
        try:
            h = json.loads(self.health_path.read_text())
            h["total_calls"] += 1
            if not success: h["failures"] += 1
            
            h["total_input_tokens"] += in_t
            h["total_output_tokens"] += out_t
            
            h["fallback_ratio"] = round(h["failures"] / h["total_calls"], 2)
            h["last_updated"] = datetime.now().isoformat()
            
            # 상태 등급 결정
            if h["fallback_ratio"] > 0.5: h["status"] = "CRITICAL"
            elif h["fallback_ratio"] > 0.1: h["status"] = "WARNING"
            else: h["status"] = "NORMAL"
            
            self.health_path.write_text(json.dumps(h, indent=2, ensure_ascii=False))
        except: pass

    def call_json_controlled(self, prompt: str, agent: str = "UNKNOWN") -> dict:
        """Control Layer가 적용된 JSON 호출 (v1.0)"""
        from src.llm.gemini_wrapper import call_gemini_with_control
        return call_gemini_with_control(self, prompt, agent)

    def call_controlled(self, prompt: str, agent: str = "UNKNOWN", max_tokens: int = 8192) -> str:
        """Control Layer가 적용된 텍스트 호출 - 503 장애 대응 재시도 포함 (v1.2)"""
        from src.llm.gemini_wrapper import log_gemini_usage
        import time

        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                # [GEMINI CALL] 텍스트 호출
                res = self.call(prompt, max_tokens=max_tokens)
                if not res: 
                    raise Exception("Empty Text Response")
                
                log_gemini_usage(agent, success=True, fallback_used=False, retry_count=attempt)
                return res

            except Exception as e:
                err_msg = str(e).lower()
                is_server_error = any(code in err_msg for code in ["503", "500", "unavailable", "overloaded"])
                
                if is_server_error and attempt < max_retries:
                    wait_time = (attempt + 1) * 3
                    print(f"  ⚠️ [GEMINI_SERVER_SURGE] 503 과부하 감지. {wait_time}초 후 재시도합니다... (Attempt {attempt+1})")
                    time.sleep(wait_time)
                    continue
                
                # 최종 실패 시
                self._update_health(success=False)
                log_gemini_usage(agent, success=False, fallback_used=True, retry_count=attempt)
                raise e
