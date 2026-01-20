import os
import sys
import traceback

try:
    from src.llm.gemini_client import GeminiClient
    print("Attempting to initialize GeminiClient...")
    client = GeminiClient()
    print("GeminiClient initialized successfully.")
except Exception:
    traceback.print_exc()
