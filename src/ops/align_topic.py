import json
from pathlib import Path

def align_topic(project_root, core_theme, topics):
    """
    Filters topics to find ones matching the core theme.
    If none found, it selects the top one and flags it for alignment.
    """
    # If topics is a single dict (like top_topic.json)
    if isinstance(topics, dict):
        if topics.get("theme") == core_theme or topics.get("selected_topic") == core_theme:
            return topics
        topics = [topics] # treat as list for processing

    filtered = [t for t in topics if t.get("theme") == core_theme or t.get("selected_topic") == core_theme]

    if filtered:
        print(f"[Aligner] Found {len(filtered)} matching topics for {core_theme}")
        return max(filtered, key=lambda x: x.get("topic_pressure", x.get("score", 0)))

    print(f"[Aligner] ⚠️ No topics match {core_theme}. Selecting top candidate as fallback.")
    if topics:
        fallback = topics[0].copy()
        fallback["theme"] = core_theme
        fallback["selected_topic"] = f"{core_theme} (Aligned)"
        return fallback
    
    return {"selected_topic": "N/A", "theme": core_theme, "topic_pressure": 0}

if __name__ == "__main__":
    sample = [{"theme": "A", "score": 0.5}, {"theme": "B", "score": 0.8}]
    print(json.dumps(align_topic(".", "B", sample), indent=2))
