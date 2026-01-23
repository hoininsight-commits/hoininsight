import json

class TopicSelector:
    def select_topics(self, candidates_data):
        """
        Selects top 1-3 topics based on scores.
        Input: Result from CandidateDetector
        """
        all_candidates = candidates_data.get("candidates", [])
        if not all_candidates:
            return {"date": candidates_data.get("date"), "topics": []}
            
        # Scoring Logic: Weighted Sum
        # Hook (40%) + WhyNow (40%) + Number (20%)
        scored_items = []
        for c in all_candidates:
            s = c.get("scores", {})
            total_score = (s.get("hook_score",0) * 0.4) + \
                          (s.get("why_now_score",0) * 0.4) + \
                          (s.get("number_score",0) * 0.2)
            c["final_score"] = total_score
            scored_items.append(c)
            
        # Sort by Score Descending
        scored_items.sort(key=lambda x: x["final_score"], reverse=True)
        
        # Pick Top 3 (ensure diversity in pools if possible - MVP skip diversity logic)
        top_picks = scored_items[:3]
        
        # Transform to Definition Format
        narrative_topics = []
        for p in top_picks:
            t = {
                "topic_id": p["candidate_id"],
                "topic_anchor": p["topic_anchor"],
                "narrative_driver": p["driver_candidates"][0] if p["driver_candidates"] else "Unspecified Driver",
                "trigger_event": p["trigger_event"],
                "core_narrative": f"{p['topic_anchor']} 현상이 {p['trigger_event']}로 인해 주목받고 있습니다. 핵심 동인은 {p.get('driver_candidates',[''])[0]}입니다.",
                "observed_metrics": p["observed_metrics"],
                "leader_stocks": p.get("driver_candidates", []),
                "intent_signals": [], # To be filled if real signal exists
                "structural_hint": "단기적 관심 확대 중",
                "era_fit": "N/A",
                "confidence_level": p["confidence"],
                "risk_note": "급격한 변동성 주의",
                "disclaimer": "This is a NARRATIVE TOPIC (Short-term Story). NOT A STRUCTURAL TOPIC."
            }
            narrative_topics.append(t)
            
        return {
            "date": candidates_data.get("date"),
            "topics": narrative_topics
        }
