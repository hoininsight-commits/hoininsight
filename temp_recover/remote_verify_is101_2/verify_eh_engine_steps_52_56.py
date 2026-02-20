import os
import json
from pathlib import Path
from datetime import datetime

from src.ops.ticker_occupancy_layer import TickerOccupancyLayer
from src.ops.reasoning_trace_layer import ReasoningTraceLayer
from src.ops.evidence_anchor_layer import EvidenceAnchorLayer
from src.ops.risk_sync_layer import RiskSyncLayer
from src.ops.narrative_output_compiler import NarrativeOutputCompiler

def main():
    base_dir = Path(".")
    run_ymd = datetime.now().strftime("%Y/%m/%d")
    
    print("\n[VERIFY] Starting Economic Hunter Engine Phase 3 Verification (Steps 52-56)")
    
    # 1. Mock Input Topic (Step 51 context)
    mock_topic = {
        "topic_id": "EH-2026-TEST",
        "title": "[구조적 병목] 2nm 파운드리 공정 지연과 장비 독점",
        "rationale": "TSMC의 수율 부진이 칩 설계사들의 로드맵 지연으로 이어지는 물리적 병목 현상.",
        "engine_conclusion": "ASML의 High-NA EUV 장비 반입 스케줄이 전체 AI 반도체 사이클의 결정적 패치가 됨.",
        "anomaly_logic": "TSMC 2nm 수율 루머 및 대만 지진 직후 장비 가동 데이터 이상 포착.",
        "bottleneck_logic": "물리적 장비(ASML)와 제조 공정(TSMC)이 결합된 하드코어 병목.",
        "why_now": {"description": "차기 AP 양산 확정 데드라인 D-90 진입."},
        "evidence": [
            {"source": "FRED", "ref_id": "BUSAPP", "value": "HIGH", "context": "신규 칩 수요 폭발 신호."},
            {"source": "DART", "ref_id": "TSMC_NOTICE", "value": "DELAY", "context": "공시 기반 일정 지연 확인."}
        ],
        "source_refs": ["news:reuters_foundry", "data:fred_123"],
        "confidence_score": 85,
        "risk_level": "LOW",
        "narrative_format": "ECONOMIC_HUNTER_VIDEO"
    }
    
    # 2. Pipeline Execution
    context = {}
    
    # Step 52 — TICKER OCCUPANCY MAP
    print("[STEP 52] Ticker Occupancy...")
    tol = TickerOccupancyLayer(base_dir)
    candidates = ["TSM", "ASML", "AAPL", "Samsung"]
    context["selected_tickers"] = tol.select_tickers(candidates, mock_topic)
    print(f" -> Selected: {[t['ticker'] for t in context['selected_tickers']]}")
    
    # Step 53 — REASONING TRACE GENERATOR
    print("[STEP 53] Reasoning Trace...")
    rtl = ReasoningTraceLayer(base_dir)
    context["reasoning_trace"] = rtl.generate_trace(mock_topic, context)
    print(f" -> Steps generated: {len(context['reasoning_trace'])}")
    
    # Step 54 — EVIDENCE ANCHOR MAPPING
    print("[STEP 54] Evidence Anchors...")
    eal = EvidenceAnchorLayer(base_dir)
    context["evidence_anchors"] = eal.map_anchors(mock_topic)
    print(f" -> Anchors mapped: {len(context['evidence_anchors'])}")
    
    # Step 55 — RISK/KILL-SWITCH FINAL SYNC
    print("[STEP 55] Risk Sync...")
    rsl = RiskSyncLayer(base_dir)
    context["sync_data"] = rsl.evaluate_sync(mock_topic, context)
    print(f" -> Status: {context['sync_data']['status']} (Conf: {context['sync_data']['final_confidence_score']})")
    
    # Step 56 — NARRATIVE OUTPUT COMPILER
    print("[STEP 56] Output Compilation...")
    noc = NarrativeOutputCompiler(base_dir)
    card = noc.compile_card(mock_topic, context)
    yaml_path = noc.save_card(card, run_ymd)
    
    # 3. Validation
    print("\n[VERIFY] Final Check...")
    if yaml_path.exists():
        print(f"[OK] Final EH Card generated at {yaml_path}")
        # Check some fields
        assert card["meta"]["status"] == "READY"
        assert len(card["targets"]) > 0
        assert len(card["trace"]) == 5
        print("[OK] Fields validation passed.")
    else:
        print("[FAIL] YAML path not found.")
        exit(1)

    print("\n[VERIFY][SUCCESS] Economic Hunter Engine Steps 52-56 Pipeline is FUNCTIONAL.")

if __name__ == "__main__":
    main()
