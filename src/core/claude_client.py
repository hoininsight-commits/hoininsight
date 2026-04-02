import anthropic
import json
import os


class ClaudeClient:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        self.model = "claude-sonnet-4-20250514"

    def call(self, prompt: str, max_tokens: int = 4000) -> str:
        """Claude API 호출"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

    def call_json(self, prompt: str, max_tokens: int = 4000) -> dict:
        """JSON 응답 파싱 포함 호출"""
        system_prompt = "너는 JSON만 출력하는 분석 엔진이다. 마크다운 코드블록 없이 순수 JSON만 출력해라."

        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        text = message.content[0].text
        text = text.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 실패: {e}")
            print(f"원본 텍스트: {text[:200]}")
            return {}
