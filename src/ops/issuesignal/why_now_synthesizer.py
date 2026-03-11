from typing import List, Dict, Any, Optional
import datetime
import logging

logger = logging.getLogger("WhyNowSynthesizer")

class WhyNowSynthesizer:
    """
    Synthesizes the "Why Now" trigger sentence for a Protagonist.
    Determines if there is a structural time pressure or inevitability.
    """

    @staticmethod
    def synthesize(protagonist: Dict[str, Any], context_events: List[Dict[str, Any]], rotation_triggered: bool, target_sector: str = "-") -> Optional[str]:
        """
        Returns a single Korean sentence explaining "Why Now?".
        Returns None if no strong timing trigger is found.
        """
        
        details = protagonist.get("details", {})
        raw_summary = details.get("raw_summary", "").lower()
        fact_date_str = protagonist.get("source_date", "")
        
        # 1. Check Keywords (Deadlines / Time Pressure)
        time_keywords = {
            "deadline": "기한 압박",
            "expire": "만료 임박",
            "effective date": "발효 시점",
            "closing": "거래 종결일",
            "immediate": "즉각적인 조치 필요",
            "terminate": "계약 종료 임박"
        }
        
        for kw, reason in time_keywords.items():
            if kw in raw_summary:
                return f"지금 이 기업이 움직일 수밖에 없는 이유는 {kw.upper()} 관련 {reason} 때문입니다."

        # 2. Check Macro/Policy Coincidence (±2 days)
        # Parse protagonist date
        try:
            p_date = datetime.datetime.strptime(fact_date_str, "%Y-%m-%d").date()
            
            for event in context_events:
                # Filter for High Grade Macro/Official
                if event.get("evidence_grade") not in ["HARD_FACT", "STRONG"]:
                    continue
                    
                e_date_str = event.get("source_date", "")
                if not e_date_str: continue
                
                # Handle varying date formats if needed, assuming YYYY-MM-DD for now as per connectors
                # Some connectors might return full datetime string, so take first 10 chars
                try:
                    e_date = datetime.datetime.strptime(e_date_str[:10], "%Y-%m-%d").date()
                    delta = abs((p_date - e_date).days)
                    
                    if delta <= 2:
                        fact_text = event.get("fact_text", "거시 이벤트")
                        # Simplify text for template
                        clean_text = fact_text.split("]")[1].strip() if "]" in fact_text else fact_text
                        if len(clean_text) > 20: clean_text = clean_text[:20] + "..."
                        
                        return f"이 행동은 외부 변수({clean_text}) 발표 시점과 맞물려 구조적으로 필연입니다."
                except:
                    continue
        except:
            pass
            
        # 3. Sector Rotation Context
        if rotation_triggered:
            return f"시장 자본이 {target_sector} 섹터로 이동하는 변곡점에서 선제적으로 단행된 행동입니다."

        # 4. Fallback: Strategic + Agreement (High Score Proxy)
        # If score is very high (>80) but no specific time keyword, valid "Strategic timing"
        score = protagonist.get("bottleneck_score", 0)
        action_type = details.get("action_type", "")
        
        if score >= 80:
             return "경쟁사가 따라올 수 없는 속도로 시장을 선점하기 위한 결정적 타이밍입니다."
             
        # Failure
        return None
