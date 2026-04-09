# src/core/claude_client.py
# GeminiClient를 ClaudeClient 이름으로 감싸는 어댑터
# 기존 에이전트 코드 수정 없이 Gemini로 전환

from dotenv import load_dotenv
load_dotenv()

try:
    from .gemini_client import GeminiClient as _Backend
    _USE_GEMINI = True
except Exception:
    _USE_GEMINI = False


class ClaudeClient:
    """
    Gemini API를 백엔드로 사용하는 클라이언트.
    기존 에이전트 코드와 호환성 유지를 위해 ClaudeClient 이름 유지.
    """

    def __init__(self):
        if not _USE_GEMINI:
            raise ImportError(
                "GeminiClient 초기화 실패. "
                "GEMINI_API_KEY 설정 및 "
                "google-generativeai 설치 여부를 확인하세요."
            )
        self._client = _Backend()
        print(f"  백엔드: Gemini ({self._client.model_name})")

    def call(self, prompt: str, max_tokens: int = 4000) -> str:
        return self._client.call(prompt, max_tokens)

    def call_json(self, prompt: str, max_tokens: int = 4000) -> dict:
        return self._client.call_json(prompt, max_tokens)
