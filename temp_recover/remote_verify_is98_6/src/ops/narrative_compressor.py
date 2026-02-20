from typing import Dict, Any, List

class NarrativeCompressor:
    """
    Step 87: Pattern → Narrative Compression.
    Converts Pattern + Replay into a 3-5 sentence compressed narrative.
    """
    
    # Banned words for safety
    BANNED_WORDS = [
        "매수", "매도", "추천", "buy", "sell", "opportunity", 
        "목표가", "target", "수익률", "return", "profit",
        "오를 것", "내릴 것", "will rise", "will fall"
    ]
    
    @staticmethod
    def compress(pattern_data: Dict[str, Any], 
                 replay_block: Dict[str, Any],
                 context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compresses pattern + replay into narrative.
        
        Args:
            pattern_data: From Step 86 (pattern detection)
            replay_block: From Step 88 (pattern memory replay)
            context: Additional context (intensity, rhythm, why_now)
        
        Returns:
            compressed_narrative: {title, body}
        """
        
        # Extract key info
        pattern_type = pattern_data.get("pattern_type", "UNKNOWN")
        pattern_narrative = pattern_data.get("narrative", "")
        
        replay_found = replay_block.get("replay_found", False)
        similar_cases = replay_block.get("similar_cases", [])
        
        intensity = context.get("intensity", "FLASH")
        why_now = context.get("why_now", "")
        
        # Build narrative following template
        
        # 1️⃣ Current detected structure
        sentence_1 = f"현재 {pattern_type.replace('_', ' ')} 패턴이 감지되었습니다."
        if pattern_narrative:
            sentence_1 = pattern_narrative
        
        # 2️⃣ Past similar pattern (if replay found)
        sentence_2 = "이 구조는 과거에 관측된 적이 없는 새로운 패턴입니다."
        if replay_found and similar_cases:
            first_case = similar_cases[0]
            first_seen = first_case.get("first_seen", "과거")[:10]  # YYYY-MM-DD
            sentence_2 = f"이와 유사한 구조가 {first_seen}에 관측된 바 있습니다."
        
        # 3️⃣ What actually happened then (outcome range)
        sentence_3 = ""
        if replay_found and similar_cases:
            outcome = similar_cases[0].get("outcome", {})
            sector_move = outcome.get("sector_movement", "TBD")
            if sector_move != "TBD":
                sentence_3 = f"당시 {sector_move} 방향으로 자본 이동이 발생했습니다."
            else:
                sentence_3 = "당시 결과는 아직 기록되지 않았으나, 구조적 긴장이 지속되었습니다."
        
        # 4️⃣ Why this pattern is surfacing now
        sentence_4 = f"현재 {intensity} 강도로 이 패턴이 재등장한 이유는 구조적 압력이 임계치에 도달했기 때문입니다."
        if why_now:
            sentence_4 = f"{why_now} 트리거로 인해 이 패턴이 지금 의미를 갖습니다."
        
        # Combine (3-5 sentences)
        body_sentences = [sentence_1, sentence_2]
        if sentence_3:
            body_sentences.append(sentence_3)
        body_sentences.append(sentence_4)
        
        body = " ".join(body_sentences)
        
        # Generate title
        title = f"{pattern_type.replace('_', ' ')} 구조 감지"
        
        # Safety check
        for word in NarrativeCompressor.BANNED_WORDS:
            if word in body or word in title:
                # Replace with neutral term
                body = body.replace(word, "[구조적 변화]")
                title = title.replace(word, "[구조]")
        
        return {
            "title": title,
            "body": body,
            "sentence_count": len(body_sentences)
        }
