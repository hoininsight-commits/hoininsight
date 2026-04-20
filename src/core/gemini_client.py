# src/core/gemini_client.py

import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 .env 명시적 로드
_ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiClient:
    """Gemini API 클라이언트 (Gemini 2.5 Flash 기반)"""

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
        """텍스트 생성 호출 (재시도 로직 포함)"""
        if not self.client:
            return ""
        
        for attempt in range(3):
            try:
                config = genai.types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                )
                if is_json:
                    config.response_mime_type = "application/json"

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                # thought_signature 포함 시 response.text에 붙는 경고문 제거를 위해 part.text만 추출
                text_parts = [part.text for part in response.candidates[0].content.parts if part.text]
                return "".join(text_parts).strip()
            except Exception as e:
                # 400 에러 중 mime_type 관련 에러는 지원하지 않는 경우이므로 일반 호출로 전환
                if "400" in str(e) and is_json:
                    return self.call(prompt, max_tokens, is_json=False)
                
                if "503" in str(e) and attempt < 2:
                    wait_time = (attempt + 1) * 2
                    print(f"  ⚠️ Gemini Busy (503). Retrying in {wait_time}s... ({attempt+1}/3)")
                    time.sleep(wait_time)
                    continue
                print(f"  Gemini API 호출 실패: {e}")
                return ""
        return ""

    def call_json(self, prompt: str, max_tokens: int = 2000) -> dict:
        import json, re
        try:
            # 1. MIME Type 설정하여 호출 시도
            response = self.call(prompt, max_tokens, is_json=True)
            if not response:
                return {}

            # 방법 1: 그대로 파싱 시도
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                pass

            # 방법 2: ```json ... ``` 블록 추출
            match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if match:
                try:
                    return json.loads(match.group(1).strip())
                except json.JSONDecodeError:
                    pass

            # 방법 3: { } 또는 [ ] 블록 추출 (가장 넓은 범위 탐색)
            # { 로 시작해서 } 로 끝나는 최상위 블록 찾기
            brace_match = re.search(r'(\{[\s\S]*\})', response)
            if brace_match:
                try:
                    return json.loads(brace_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # [ 로 시작해서 ] 로 끝나는 최상위 블록 찾기
            bracket_match = re.search(r'(\[[\s\S]*\])', response)
            if bracket_match:
                try:
                    return json.loads(bracket_match.group(1))
                except json.JSONDecodeError:
                    pass

            # 방법 4: 복구 시도 (미완성 블록)
            match = re.search(r'(\{[\s\S]*|\[[\s\S]*)', response)
            if match:
                try:
                    raw_json = match.group(0).strip()
                    # 열린 괄호 수만큼 닫기
                    open_braces = raw_json.count('{') - raw_json.count('}')
                    open_brackets = raw_json.count('[') - raw_json.count(']')
                    
                    if raw_json.endswith(','):
                        raw_json = raw_json[:-1]
                        
                    raw_json += ']' * max(0, open_brackets) + '}' * max(0, open_braces)
                    return json.loads(raw_json)
                except Exception:
                    pass

            print(f"  ⚠️ JSON 파싱 전부 실패. 응답 길이: {len(response)}")
            print(f"  응답 마지막 100자: {response[-100:]}")
            return {}

        except Exception as e:
            print(f"  ❌ call_json 오류: {e}")
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
