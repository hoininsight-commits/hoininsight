# src/core/gemini_client.py

import json
import os
import time
from pathlib import Path
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
        
        # [DEBUG] 종료 사유 분석
        reason = response.candidates[0].finish_reason
        if reason != "STOP":
            print(f"  ⚠️ Gemini Finish Reason: {reason} | Model: {self.model_name}")

        # text 파트 추출
        text_parts = [part.text for part in response.candidates[0].content.parts if part.text]
        result = "".join(text_parts).strip()
        
        # [DEBUG] 마지막 응답 캡처
        try:
            (DEBUG_DIR / "last_raw_response.txt").write_text(result, encoding='utf-8')
        except: pass
        
        return result

    def call_json(self, prompt: str, max_tokens: int = 2500) -> dict:
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

    def call_json_controlled(self, prompt: str, agent: str = "UNKNOWN") -> dict:
        """Control Layer가 적용된 JSON 호출 (v1.0)"""
        from src.llm.gemini_wrapper import call_gemini_with_control
        return call_gemini_with_control(self, prompt, agent)

    def call_controlled(self, prompt: str, agent: str = "UNKNOWN", max_tokens: int = 4000) -> str:
        """Control Layer가 적용된 텍스트 호출 (로깅 포함)"""
        from src.llm.gemini_wrapper import log_gemini_usage
        try:
            res = self.call(prompt, max_tokens=max_tokens)
            if not res: raise Exception("Empty Text Response")
            log_gemini_usage(agent, success=True, fallback_used=False, retry_count=0)
            return res
        except Exception as e:
            log_gemini_usage(agent, success=False, fallback_used=True, retry_count=0)
            raise e
