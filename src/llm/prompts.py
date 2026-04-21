# src/llm/prompts.py

STRICT_JSON_PROMPT = """
[STRICT JSON PROTOCOL]
1. Return ONLY valid JSON.
2. Do not include explanation or markdown tags (e.g., ```json).
3. Do not include extra text before or after the JSON block.
4. Ensure all fields are present according to the schema.
"""
