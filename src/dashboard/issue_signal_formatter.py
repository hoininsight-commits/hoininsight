from typing import Dict, Any, List
import re

class IssueSignalFormatter:
    """
    Step 68: Issue Signal Display Refinement (Operator-First UI)
    - Deterministic Korean Title Generation
    - Minimum Script Template Enforcement
    - reliability Badge Logic
    """
    
    # Deterministic Keyword Map for Title Generation
    # English Keyword -> Korean Context
    KEYWORD_MAP = {
        "mandates": "의무화",
        "standard": "표준",
        "comply": "규제 준수",
        "alliance": "연합",
        "redefine": "재정의",
        "supply chain": "공급망",
        "shift": "전환",
        "split": "분할",
        "spin-off": "물적분할",
        "dilution": "가치 희석",
        "export": "수출",
        "regulation": "규제",
        "tariff": "관세",
        "tax": "세금",
        "subsidy": "보조금",
        "infrastructure": "인프라",
        "shortage": "공급 부족",
        "surplus": "공급 과잉",
        "demand": "수요",
        "inventory": "재고",
        "cycle": "사이클"
    }

    @staticmethod
    def format_card(card: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance the card dictionary with UI-specific fields.
        Does NOT modify original fields, adds *_display fields.
        """
        original_title = card.get('title', '')
        
        # 1. Generate Korean Title
        title_ko = IssueSignalFormatter._generate_korean_title(original_title, card.get('structure_type'))
        
        # 2. Generate Badge
        badge_html = IssueSignalFormatter._generate_reliability_badge(card)
        
        # 3. Generate Script Sections
        script_sections = IssueSignalFormatter._generate_script_sections(card)
        
        return {
            **card,
            "title_display": title_ko,
            "badge_display": badge_html,
            "script_sections": script_sections,
            "raw_title": original_title  # Keep original for reference
        }

    @staticmethod
    def _generate_korean_title(text: str, structure_type: str) -> str:
        """Rule-based Title Translation/Mapping"""
        if not text:
            return "제목 없음"
            
        # Check if already Korean (simple check)
        if re.search("[가-힣]", text):
            return text
            
        text_lower = text.lower()
        matched_keywords = []
        
        for k, v in IssueSignalFormatter.KEYWORD_MAP.items():
            if k in text_lower:
                matched_keywords.append(v)
        
        # Construct Title based on Structure Type
        prefix = "구조적 이슈"
        if structure_type == "STRUCTURAL_DAMAGE":
            prefix = "구조적 피해 경고"
        elif structure_type == "STRUCTURAL_REDEFINITION":
            prefix = "산업 구조 재정의"
            
        if matched_keywords:
            # "산업 구조 재정의: 공급망, 의무화 패턴"
            keywords_str = ", ".join(matched_keywords[:2]) # Max 2 keywords
            return f"{prefix}: {keywords_str} 패턴 감지"
        else:
            # Fallback
            return f"{prefix}: 글로벌 시그널 감지"

    @staticmethod
    def _generate_reliability_badge(card: Dict[str, Any]) -> str:
        """
        [✅ 실데이터] vs [🧪 테스트/입력]
        Rule: source_refs >= 1 AND no 'test' in IDs -> Real
        """
        refs = card.get('evidence_refs', {})
        ids = refs.get('source_ids', [])
        
        is_test = False
        if not ids:
            is_test = True
        else:
            for sid in ids:
                if "test" in sid.lower() or "input" in sid.lower():
                    is_test = True
                    break
        
        if is_test:
            return '<span class="meta-item" style="color:#f59e0b; border:1px solid #f59e0b; padding:0 4px; border-radius:4px; font-size:10px;">🧪 테스트/입력</span>'
        else:
            return '<span class="meta-item" style="color:#10b981; border:1px solid #10b981; padding:0 4px; border-radius:4px; font-size:10px;">✅ 실데이터</span>'

    @staticmethod
    def _generate_script_sections(card: Dict[str, Any]) -> str:
        """
        Generate strict 4-section script HTML.
        1. Why Now
        2. Structural Change
        3. Data Drivers
        4. Risk
        """
        # Extract existing generated natural text if available
        # But we enforce structure here.
        
        # 1. Why Now
        # Try to find 'market_misunderstanding' or 'why_now' from raw card if available, 
        # but IssueSignal card has 'script_natural' which is a blob.
        # We process 'script_natural' or fallback.
        
        raw_script = card.get('script_natural', '')
        why_now = "변화의 트리거가 감지되었습니다." 
        if "지금 이 이슈를 주목해야 하는 이유" in raw_script:
             # Basic extraction heuristic or just use the full blob if parsing fails
             pass
             
        # Use simple mapping from available fields
        summary = card.get('one_line_summary', '요약 없음')
        rationale = card.get('rationale_natural', '-')
        
        risk = card.get('evidence_refs', {}).get('risk_factor', '확인 필요')
        drivers = card.get('evidence_refs', {}).get('structural_drivers', [])
        drivers_str = ", ".join(drivers) if drivers else "식별된 드라이버 없음"
        
        return f"""
        <div class="detail-section">
            <h3>⚡ 왜 지금 봐야 하나 (Why Now)</h3>
            <p>{rationale}</p>
        </div>
        <div class="detail-section">
            <h3>🔄 어떤 구조가 바뀌었나 (Change)</h3>
            <p>{summary}</p>
        </div>
        <div class="detail-section">
            <h3>📊 근거 데이터 (Drivers)</h3>
            <ul class="data-list">
                <li><strong>운영기제:</strong> {drivers_str}</li>
                <li><strong>참조 ID:</strong> {len(card.get('evidence_refs', {}).get('source_ids', []))}건</li>
            </ul>
        </div>
        <div class="detail-section">
            <h3>⚠️ 리스크 / 확인 포인트</h3>
            <p>{risk}</p>
        </div>
        """
