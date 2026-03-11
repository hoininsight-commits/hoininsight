from pathlib import Path
from typing import Dict, Any

class PreTriggerLayer:
    """
    (IS-11) Detects "about-to-trigger" states and assigns PRE_TRIGGER status.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        
    def classify_state(self, signal: Dict[str, Any]) -> str:
        """
        Classifies signal into WATCH, PRE_TRIGGER, or TRIGGER.
        """
        content = signal.get("content", "").lower()
        importance = signal.get("importance", "LOW")
        
        # 1. TRIGGER Conditions (Immediate impact/Official)
        if "official" in content or "signed" in content or importance == "CRITICAL":
            return "TRIGGER"
            
        # 2. PRE_TRIGGER Conditions (Unavoidable precursor with Commitment)
        if importance == "HIGH" and any(kw in content for kw in ["committee", "passed", "upcoming"]):
            return "PRE_TRIGGER"
            
        # 3. WATCH (Interest but not locked)
        return "WATCH"

    def generate_watch_narrative(self, signal: Dict[str, Any]) -> str:
        """
        Generates narrative for PRE_TRIGGER signals.
        """
        return f"WATCH ALERT: '{signal.get('content')}' is approaching a structural threshold. No tickers selected yet, but capital movement convergence is expected soon."

class PreTriggerEngine:
    """
    (IS-21) Generates authoritative pre-emptive content for inevitable events.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def generate_pre_content(self, data: Dict[str, Any]) -> str:
        """
        Generates the mandatory 8-block structure if criteria are met.
        """
        if not self._validate_criteria(data):
            return ""

        blocks = []
        
        # 1. OPENING
        blocks.append(f"시장은 아직 평온하나, {data.get('event')}의 그림자는 이미 거대하다. 지금의 침묵은 평화가 아닌 태풍 전야의 병목 상태다.")
        
        # 2. WHY PEOPLE FEEL SAFE
        blocks.append("사람들이 안심하는 이유는 명확하다. 아직 공식적인 발표나 직접적인 충격이 눈에 보이지 않기 때문이다.")
        
        # 3. WHY THAT IS WRONG
        blocks.append("하지만 이것은 구조적 착각이다. 자본은 이미 대안 없는 골목으로 스스로를 몰아넣고 있다.")
        
        # 4. LOCKED CONDITION
        blocks.append(f"구조적 경로는 이미 고착되었다. {data.get('locked_reason')} 때문에 더 이상 되돌릴 수 없는 지점을 넘어섰다.")
        
        # 5. PRE-TRIGGER SENTENCE (Template)
        blocks.append(f"아직 {data.get('event')}은 터지지 않았지만, {data.get('actor')}는 이미 {data.get('action')}을 해야 하는 상태다.")
        
        # 6. CAPITAL COMMITMENT
        blocks.append(f"증거는 명확하다. 이미 {data.get('commitment')}이 집행되었으며, 이는 돌려받을 수 없는 매몰 비용이자 선행 행동이다.")
        
        # 7. BOTTLENECK & TICKERS
        tickers = data.get("tickers", [])
        ticker_lines = [f"- {t['ticker']}: {t.get('rationale', '병목 지배력을 가진 핵심 수혜주이다.')}" for t in tickers[:3]]
        blocks.append("\n".join(ticker_lines))
        
        # 8. EARLY KILL SWITCH
        blocks.append(f"PRE-TRIGGER 무효화 시그널: {data.get('kill_switch_signal')}")

        return "\n\n".join(blocks)

    def _validate_criteria(self, data: Dict[str, Any]) -> bool:
        """
        Strict validation for PRE-TRIGGER status.
        """
        required = ["event", "actor", "action", "locked_reason", "commitment", "kill_switch_signal"]
        if not all(k in data for k in required):
            return False
            
        # Forbidden check
        forbid = ["될 것이다", "할 예정이다", "가능성", "확률"]
        text = str(data)
        if any(f in text for f in forbid):
            return False
            
        return True
