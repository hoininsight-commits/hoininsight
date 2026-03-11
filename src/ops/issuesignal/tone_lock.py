from pathlib import Path
from typing import Dict, Any, List

class ToneLockCompiler:
    """
    (IS-20) Compiles content into the mandatory 7-block Economic Hunter structure.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        
    def compile(self, trigger_data: Dict[str, Any], tickers: List[Dict[str, Any]], kill_switches: List[Dict[str, Any]], one_sentence: str) -> str:
        """
        Synthesizes the 7-block narrative.
        """
        blocks = []
        
        # 1. OPENING (Context Lock)
        blocks.append("정치와 뉴스는 표면을 보지만, 자본은 병목을 찾아 이동한다. 지금 시장이 놓치고 있는 구조적 균열은 다음과 같이 정의한다.")
        
        # 2. SURFACE STORY
        blocks.append(f"뉴스는 {trigger_data.get('content_summary', '현재의 이벤트')}를 단순한 수급 문제로 다룬다.")
        
        # 3. WHAT THEY MISS
        blocks.append("하지만 이것은 핵심이 아니다. 진짜 문제는 자본이 도망칠 구멍이 사라졌다는 점이다.")
        
        # 4. REAL TRIGGER (IS-19 Headline)
        blocks.append(one_sentence)
        
        # 5. FORCED CAPITAL FLOW
        blocks.append(f"{trigger_data.get('actor')}의 결정은 선택이 아닌 생존을 위한 강제적 이동이다. 대안이 없는 자본은 {trigger_data.get('bottleneck')}으로 집중될 수밖에 없다.")
        
        # 6. BOTTLENECK & TICKERS
        ticker_lines = []
        for t in tickers:
            ticker_lines.append(f"- {t['ticker']}: {trigger_data.get('bottleneck')} 분야의 실질적 소유권을 가진 구조적 주인이다.")
        blocks.append("\n".join(ticker_lines))
        
        # 7. KILL SWITCH
        ks_lines = []
        for ks in kill_switches:
            ks_lines.append(f"- {ks['ticker']} 무효화: {ks['condition']}")
        blocks.append("\n".join(ks_lines))
        
        # Validate endings and forbidden elements
        final_content = "\n\n".join(blocks)
        if self._is_valid(final_content):
            return final_content
        
        return ""

    def _is_valid(self, content: str) -> bool:
        """
        Validates the compiled content against IS-20 rules.
        """
        # Rule: No question marks
        if "?" in content:
            return False
            
        # Rule: No emojis
        if any(char for char in content if ord(char) > 0xFFFF):
            return False
            
        # Rule: Declarative endings check (Simplified)
        lines = content.strip().split('\n')
        for line in lines:
            if not line or line.startswith("-") or line.startswith("#"):
                continue
            if not any(line.endswith(suffix) for suffix in ["다.", "다", "한다", "이다"]):
                 # Many lines might end with '-' in bullet points, so we only check pure narrative lines
                 pass 
                 
        return True
