# src/llm/gemini_control_map.py
# HOIN Insight Gemini Control Layer - Responsibility Map

GEMINI_RESPONSIBILITY = {
    "DETECTOR": [
        "news_structuring",
        "narrative_candidate_generation"
    ],
    "ANALYST": [
        "causal_chain_generation",
        "scenario_expansion"
    ],
    "WRITER": [
        "script_generation"
    ]
}

GEMINI_AUTHORITY_LEVEL = {
    "DETECTOR": "ASSIST",
    "ANALYST": "CO-PILOT",
    "WRITER": "PRIMARY"
}
