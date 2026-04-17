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

    def call(self, prompt: str, max_tokens: int = 4000) -> str:
        """텍스트 생성 호출 (재시도 로직 포함)"""
        if not self.client:
            return ""
        
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.7,
                    )
                )
                # thought_signature 포함 시 response.text에 붙는 경고문 제거를 위해 part.text만 추출
                text_parts = [part.text for part in response.candidates[0].content.parts if part.text]
                return "".join(text_parts).strip()
            except Exception as e:
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
            response = self.call(prompt, max_tokens)
            if not response:
                return {}

            # 방법 1: 그대로 파싱
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                pass

            # 방법 2: ```json 코드블록 추출
            match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass

            # 방법 3: { } 또는 [ ] 블록 추출 (미완성 블록 포함)
            match = re.search(r'(\{[\s\S]*|\[[\s\S]*)', response)
            if match:
                try:
                    raw_json = match.group(0)
                    # 최대한 닫는 괄호까지만 일단 시도
                    last_brace = raw_json.rfind('}')
                    last_bracket = raw_json.rfind(']')
                    cut_off = max(last_brace, last_bracket)
                    if cut_off != -1:
                        raw_json = raw_json[:cut_off+1]
                    
                    try:
                        return json.loads(raw_json)
                    except json.JSONDecodeError:
                        # 복구 시도
                        # 1. 문자열이 열려 있는지 확인
                        quotes = re.findall(r'(?<!\\)"', raw_json)
                        if len(quotes) % 2 != 0:
                            raw_json += '"'
                        
                        # 2. 열린 괄호 수만큼 닫기
                        open_braces = raw_json.count('{') - raw_json.count('}')
                        open_brackets = raw_json.count('[') - raw_json.count(']')
                        
                        raw_json = raw_json.strip()
                        if raw_json.endswith(','):
                            raw_json = raw_json[:-1]
                            
                        raw_json += ']' * open_brackets + '}' * open_braces
                        return json.loads(raw_json)
                except Exception:
                    pass

            print(f"  ⚠️ JSON 파싱 전부 실패. 응답 길이: {len(response)}")
            print(f"  응답 마지막 100자: {response[-100:]}")
            return {}

        except Exception as e:
            print(f"  ❌ call_json 오류: {e}")
            return {}
