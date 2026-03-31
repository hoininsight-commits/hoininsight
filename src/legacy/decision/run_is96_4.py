from src.decision.assembler import run_decision_assembly
import uuid
from datetime import datetime

def main():
    print(">>> Starting IS-96-4 Decision Output Assembly (Add-only)...")
    
    # 1. Synthetic Interpretation Units (Mocking IS-96-1 outputs)
    units = [
        {
            "interpretation_id": str(uuid.uuid4()),
            "as_of_date": datetime.now().strftime("%Y-%m-%d"),
            "target_sector": "TECH_INFRA_KOREA",
            "interpretation_key": "STRUCTURAL_ROUTE_FIXATION",
            "why_now_type": "Schedule-driven",
            "confidence_score": 0.88,
            "evidence_tags": ["KR_POLICY", "PRETEXT_VALIDATION", "EARNINGS_VERIFY"],
            "structural_narrative": "정책 예산 집행과 기업 실적 발표가 맞물리며 Tech 인프라 섹터의 구조적 반등 시발점이 확인됨.",
            "derived_metrics_snapshot": {"pretext_score": 0.92, "policy_commitment_score": 0.85}
        },
        {
            "interpretation_id": str(uuid.uuid4()),
            "as_of_date": datetime.now().strftime("%Y-%m-%d"),
            "target_sector": "FINANCIAL_VALUE_UP",
            "interpretation_key": "FUNDAMENTAL_RE-RATING",
            "why_now_type": "State-driven",
            "confidence_score": 0.75,
            "evidence_tags": ["KR_POLICY", "FLOW_ROTATION"],
            "structural_narrative": "자율 공시 도입 기대감으로 자본 유입이 관찰되나 실적 검증 데이터는 대기 상태.",
            "derived_metrics_snapshot": {"pretext_score": 0.78}
        }
    ]

    # 2. Loading Live Catalyst Events (IS-96-5b Wiring)
    import json
    from pathlib import Path
    catalyst_events = []
    catalyst_path = Path("data/ops/catalyst_events.json")
    if catalyst_path.exists():
        with open(catalyst_path, "r", encoding="utf-8") as f:
            catalyst_events = json.load(f)
        print(f"[OK] Loaded {len(catalyst_events)} catalyst events.")

    # 3. Run Assembly
    run_decision_assembly(units, catalyst_events=catalyst_events)
    print("<<< IS-96-4 Assembly Complete.")

if __name__ == "__main__":
    main()
