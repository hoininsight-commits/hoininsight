import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    print("🔍 가용 모델 리스트 조회 중...")
    # 모델 객체의 모든 속성을 출력해서 정확한 명칭 확인
    for model in client.models.list():
        print(f"Model: {model}")
except Exception as e:
    print(f"❌ 오류 발생: {e}")
