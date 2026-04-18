import os
from google import genai
from dotenv import load_dotenv
from pathlib import Path

_ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(_ENV_PATH)
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
print("Listing models (v1)...")
try:
    for m in client.models.list():
        print(f"{m.name}")
except Exception as e:
    print(f"Error v1: {e}")
