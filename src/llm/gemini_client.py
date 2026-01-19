import os
import google.generativeai as genai
from typing import Optional
from dotenv import load_dotenv

 # Load environment variables from .env file
load_dotenv()

class GeminiClient:
    def __init__(self):
        # Explicitly reload to be sure
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def generate_content(self, prompt: str) -> Optional[str]:
        """
        Generates content using Gemini 1.5 Pro.
        Returns the text response or None if failed.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"[GeminiClient] Error: {e}")
            return None
