from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

def _ymd_iso() -> str:
    return datetime.utcnow().isoformat()

def _ymd_slashed() -> str:
    return datetime.utcnow().strftime("%Y/%m/%d")

def _ymd_dashed() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")

def _read_json(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

from src.ops.content_gate import evaluate_content_gate

def generate_insight_content(base_dir: Path) -> None:
    # [Ops Upgrade v1.1] Content Gate Check
    gate = evaluate_content_gate(base_dir)
    allow = gate.get("allow_content", False)
    mode = gate.get("content_mode", "SKIP")
    reason = gate.get("reason", "Unknown")
    
    out_dir = base_dir / "data" / "content"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if not allow:
        # Generate content_skipped.md
        skipped_lines = []
        skipped_lines.append("# Content Generation Skipped")
        skipped_lines.append("")
        skipped_lines.append(f"- **Mode**: {mode}")
        skipped_lines.append(f"- **Reason**: {reason}")
        skipped_lines.append("- **Timestamp**: " + datetime.utcnow().isoformat())
        
        (out_dir / "content_skipped.md").write_text("\n".join(skipped_lines), encoding="utf-8")
        print(f"[INFO] Content generation SKIPPED. Mode={mode}")
        return

    # If allowed, proceed with generation...
    ymd = _ymd_slashed()
    ymd_dash = _ymd_dashed()
    
    # 1. Load Regime History (Define current_regime FIRST)
    hist_path = base_dir / "data" / "regimes" / "regime_history.json"
    history_data = _read_json(hist_path)
    current_regime = "Unknown"
    persistence_days = 1
    if history_data and "history" in history_data:
         entries = history_data["history"]
         if entries:
             last = entries[-1]
             current_regime = last.get("regime", "Unknown")
             streak = 0
             for e in reversed(entries):
                 if e["regime"] == current_regime:
                     streak += 1
                 else:
                     break
             persistence_days = streak
    
    # [Ops Upgrade v1.2] Content Preset Selection
    from src.ops.content_preset_selector import select_content_preset
    
    # Check Meta Topic Existence
    meta_path = base_dir / "data" / "meta_topics" / ymd / "meta_topics.json"
    has_meta = False
    if meta_path.exists():
        try:
            has_meta = len(json.loads(meta_path.read_text())) > 0
        except: pass

    # Get Confidence
    from src.ops.regime_confidence import calculate_regime_confidence
    conf_res = calculate_regime_confidence(base_dir / "data" / "dashboard" / "collection_status.json")
    conf_val = conf_res.get("regime_confidence", "LOW")
    
    # Call Selector
    preset_res = select_content_preset(current_regime, conf_val, has_meta)
    preset = preset_res.get("preset", "STANDARD")
    preset_reason = preset_res.get("reason", "")
    
    # 2. Drift Signals
    drift_path = base_dir / "data" / "narratives" / "narrative_drift_v1.json"
    drift_data = _read_json(drift_path)
    current_drifts = []
    if drift_data and "history" in drift_data:
        drift_hist = drift_data.get("history", [])
        if drift_hist:
            last_drift = drift_hist[-1]
            current_drifts = last_drift.get("drifts", [])

    # 3. Strategy
    from src.strategies.regime_strategy_resolver import resolve_strategy_frameworks
    strat_info = resolve_strategy_frameworks(base_dir, current_regime, persistence_days)
    frameworks = strat_info.get("strategy_frameworks", [])
    
    # Generate Script
    script_lines = []
    script_lines.append(f"# Insight Script ({ymd_dash})")
    script_lines.append(f"<!-- Metadata")
    script_lines.append(f"Content Mod: {mode}")
    script_lines.append(f"Content Preset: {preset}")
    script_lines.append(f"Preset Reason: {preset_reason}")
    script_lines.append(f"Confidence: {conf_val}")
    script_lines.append(f"Regime: {current_regime}")
    script_lines.append(f"-->")
    script_lines.append("")
    
    script_lines.append("## Opening (Context)")
    
    # [Ops Upgrade v1.1] Cautious Mode Warning
    if mode == "CAUTIOUS":
        script_lines.append("> [!WARNING] Cautious Mode")
        script_lines.append("> ※ 일부 핵심 데이터가 제한된 상태에서 생성된 참고용 인사이트입니다.")
        script_lines.append("")
        
    script_lines.append(f"- 오늘 감지된 시장의 핵심 국면은 **{current_regime}**입니다.")
    if preset != "BRIEF":
        script_lines.append("- 단순한 뉴스나 가격 변동이 아닌, 데이터가 가리키는 구조적 흐름입니다.")
    script_lines.append("")
    
    script_lines.append("## Why Now")
    script_lines.append(f"- 이 국면은 현재 **{persistence_days}일째** 지속되고 있습니다.")
    
    drift_items = [d for d in current_drifts if d.get("entity_id") == current_regime]
    drift_summary = "특이 사항 없음"
    if drift_items:
        d = drift_items[0]
        dtype = d.get("drift_type", "NONE")
        drift_summary = f"현재 Narrative 상태는 **{dtype}** 단계입니다."
    
    # Brief: Only show if drift exists
    if preset == "BRIEF":
        if drift_items:
             script_lines.append(f"- {drift_summary}")
    else:
        script_lines.append(f"- {drift_summary}")
        
    script_lines.append("")
    
    # Section: What Changed (Standard/Deep Only)
    if preset in ["STANDARD", "DEEP"]:
        script_lines.append("## What Changed")
        script_lines.append("- 과거 데이터와 비교했을 때, 주제의 빈도와 강도가 유의미하게 변화했습니다.")
        if persistence_days > 1:
            script_lines.append("- 일회성 이슈를 넘어 추세적 성격을 띠기 시작했습니다.")
        else:
            script_lines.append("- 새로운 흐름이 포착되었습니다.")
        script_lines.append("")

    # Section: Mechanism (Deep Only)
    if preset == "DEEP":
        script_lines.append("## Mechanism (Deep Dive)")
        script_lines.append("- 이 국면의 기저에는 거시경제적 자금 흐름과 정책적 요인이 복합적으로 작용하고 있습니다.")
        script_lines.append("- (자동 생성된 심층 분석 Placeholder: 상관관계 및 인과성 추적)")
        script_lines.append("")

    script_lines.append("## What to Watch (Neutral)")
    script_lines.append("- 이 국면에서 유효한 관찰 프레임워크는 다음과 같습니다:")
    
    # Limit frameworks based on preset
    visible_fw = frameworks
    if preset == "BRIEF":
        visible_fw = frameworks[:1] # Max 1
    
    if visible_fw:
        for fw in visible_fw:
             script_lines.append(f"  * **{fw.get('name')}**: {', '.join(fw.get('focus', []))}")
    else:
        script_lines.append("  * (특정 전략 프레임워크 없음)")
        
    if preset == "BRIEF" and len(frameworks) > 1:
        script_lines.append(f"  * (외 {len(frameworks)-1}개 프레임워크 생략됨)")

    script_lines.append("")
    
    script_lines.append("## Closing")
    script_lines.append("- 지금의 국면을 이해하는 것이 시장의 소음을 걸러내는 첫걸음입니다.")
    
    # Generate Shotlist (Adjusted by Preset)
    shotlist_lines = []
    shotlist_lines.append(f"# Insight Shotlist ({ymd_dash})")
    shotlist_lines.append(f"Preset: {preset}")
    shotlist_lines.append("")
    
    # Shot 1: Opening
    shotlist_lines.append("1. Opening")
    shotlist_lines.append(f"   - 화면: **{current_regime}** 키워드 강조 타이틀")
    shotlist_lines.append(f"   - 자막: 오늘의 Market Regime: {current_regime}")
    shotlist_lines.append("")
    
    # Shot 2: Why Now
    shotlist_lines.append("2. Why Now")
    shotlist_lines.append(f"   - 화면: Persistence 타임라인 ({persistence_days} days)")
    if preset != "BRIEF":
        shotlist_lines.append("   - 화면: Narrative Drift 상태 아이콘")
    shotlist_lines.append("")
    
    shot_idx = 3
    
    # Shot 3: What Changed (Standard/Deep)
    if preset in ["STANDARD", "DEEP"]:
        shotlist_lines.append(f"{shot_idx}. What Changed")
        shotlist_lines.append("   - 화면: Topic / Meta Topic 변화 비교")
        shotlist_lines.append("   - 화면: 빈도/지속성 변화 차트")
        shotlist_lines.append("")
        shot_idx += 1
        
    # Shot 4: Mechanism (Deep)
    if preset == "DEEP":
        shotlist_lines.append(f"{shot_idx}. Deep Dive")
        shotlist_lines.append("   - 화면: 상관관계 히트맵 / 매크로 지표 오버레이")
        shotlist_lines.append("   - 자막: “시장 역학의 구조적 원인”")
        shotlist_lines.append("")
        shot_idx += 1

    # Shot 5: What to Watch
    shotlist_lines.append(f"{shot_idx}. What to Watch")
    if visible_fw:
        kws = [f.get("name") for f in visible_fw]
        shotlist_lines.append(f"   - 화면: 키워드 나열 ({', '.join(kws)})")
    else:
        shotlist_lines.append("   - 화면: 관찰 키워드 없음")
    shotlist_lines.append("   - 자막: “Observation Framework”")
    shotlist_lines.append("")
    shot_idx += 1
    
    # Shot 6: Closing
    shotlist_lines.append(f"{shot_idx}. Closing")
    shotlist_lines.append("   - 화면: 핵심 요약 문장")
    
    # Write Files
    out_dir = base_dir / "data" / "content"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    (out_dir / "insight_script_v1.md").write_text("\n".join(script_lines), encoding="utf-8")
    (out_dir / "insight_shotlist_v1.md").write_text("\n".join(shotlist_lines), encoding="utf-8")
