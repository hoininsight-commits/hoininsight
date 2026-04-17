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
    """Gemini API 클라이언트 — Claude API 대체"""

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

    def call_json(self, prompt: str, max_tokens: int = 4000) -> dict:
        """JSON 응답 파싱 포함 호출"""
        if not self.client:
            return {}
        system_instruction = (
            "너는 JSON만 출력하는 분석 엔진이다. "
            "마크다운 코드블록 없이 순수 JSON만 출력해라. "
            "다른 설명이나 텍스트는 절대 포함하지 마라."
        )

        full_prompt = f"{system_instruction}\n\n{prompt}"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.3,
                )
            )
            # thought_signature 등이 포함된 경우 response.text에 경고문이 붙으므로 part.text만 추출
            text_parts = [part.text for part in response.candidates[0].content.parts if part.text]
            text = "".join(text_parts).strip()
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)

        except json.JSONDecodeError as e:
            print(f"  JSON 파싱 실패: {e}")
            # text 변수가 정의되지 않았을 경우를 위한 방어 코드
            raw_text = "".join([p.text for p in response.candidates[0].content.parts if p.text]) if 'response' in locals() else "N/A"
            print(f"  원본 텍스트: {raw_text[:200]}")
            return {}
        except Exception as e:
            print(f"  Gemini API 호출 실패: {e}")
            return {}
