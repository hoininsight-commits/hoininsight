# src/llm/failure_types.py

FAILURE_TYPES = [
    "RATE_LIMIT",        # 429
    "SERVER_ERROR",      # 5xx
    "TIMEOUT",
    "JSON_PARSE_ERROR",
    "CONTRACT_FAIL",
    "EMPTY_RESPONSE",
    "LOW_QUALITY",
    "UNKNOWN"
]
