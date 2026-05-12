import os
import sys
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    print("No API Key")
    sys.exit(1)

client = genai.Client(api_key=api_key)

models_to_test = [
    'gemini-1.5-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash-001',
    'gemini-1.5-flash-002',
    'gemini-2.0-flash-exp'
]

for m in models_to_test:
    try:
        print(f"Testing {m}...", end=" ")
        res = client.models.generate_content(model=m, contents="Say hello.")
        print(f"SUCCESS: {res.text.strip()}")
    except Exception as e:
        print(f"FAIL: {e}")
