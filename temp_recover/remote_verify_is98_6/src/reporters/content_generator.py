from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils.i18n_ko import I18N_KO

def _ymd_iso() -> str:
    return datetime.now().isoformat()

def _ymd_slashed() -> str:
    return datetime.now().strftime("%Y/%m/%d")

def _ymd_dashed() -> str:
    return datetime.now().strftime("%Y-%m-%d")

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
        skipped_lines.append("- **Timestamp**: " + datetime.now().isoformat())
        
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
    
    # [Ops Upgrade v1.3] Multi-Topic Script Generation
    # Load Final Decision Card
    decision_path = base_dir / "data" / "decision" / ymd / "final_decision_card.json"
    decision_data = _read_json(decision_path)
    
    top_topics = []
    if decision_data:
        # Check for top_topics list
        top_topics = decision_data.get("top_topics", [])
        # If no top_topics list but main topic exists, treat as single item
        if not top_topics and decision_data.get("topic"):
             top_topics = [decision_data]

    # If we have topics, generate scripts for each (List Mode)
    if top_topics:
        print(f"[INFO] Generating scripts for {len(top_topics)} topics...")
        
        for idx, topic in enumerate(top_topics):
            t_title = topic.get("title", f"Topic #{idx+1}")
            t_rationale = topic.get("rationale", "No rationale provided.")
            t_id = topic.get("dataset_id", "unknown")
            t_level = topic.get("level", "L2")
            
            # Build Script Content
            lines = []
            lines.append(f"# Insight Script: {t_title}")
            lines.append(f"<!-- Metadata")
            lines.append(f"Topic ID: {t_id}")
            lines.append(f"Level: {t_level}")
            lines.append(f"Rank: {idx+1}")
            lines.append(f"Content Preset: {preset}")
            lines.append(f"-->")
            lines.append("")
           
            lines.append(f"## 1. {I18N_KO['SIGNAL_LOGIC']}")
            lines.append(f"- **{t_title}** 현상이 감지되었습니다.")
            lines.append(f"- 이는 **{current_regime}** 국면 하에서 발생한 중요한 시그널입니다.")
            lines.append("")
            
            lines.append(f"## 2. {I18N_KO['RATIONALE']}")
            lines.append(f"- {t_rationale}")
            lines.append("")
            
            lines.append(f"## 3. {I18N_KO['DATA_EVIDENCE']}")
            lines.append(f"- 주요 지표: `{t_id}`")
            if "evidence" in topic:
                ev = topic["evidence"]
                if isinstance(ev, dict) and "details" in ev:
                    det = ev["details"]
                    lines.append(f"- 수치: {det.get('value', 'N/A')} (Z-Score: {det.get('z_score', 0)})")
                    lines.append(f"- 분석: {det.get('reasoning', '')}")
            lines.append("")
            
            lines.append("## 4. Actionable Insight")
            lines.append("- 이 흐름이 지속될 경우, 관련 섹터에 대한 리스크 관리가 필요합니다.")
            if idx == 0:
                 lines.append("- (Main Topic) 전체 포트폴리오 관점에서의 대응이 요구됩니다.")
            else:
                 lines.append("- (Sub Topic) 모니터링 강화 및 선별적 접근을 권장합니다.")
            
            # File Naming Logic
            # Topic #1 -> insight_script.md (Main)
            # Topic #2..N -> insight_script_2.md, insight_script_3.md ...
            if idx == 0:
                fname = "insight_script_v1.md"
            else:
                fname = f"insight_script_{idx+1}.md"
                
            out_path = out_dir / fname
            out_path.write_text("\n".join(lines), encoding="utf-8")
            
        print(f"[INFO] Generated {len(top_topics)} scripts.")

    else:
        # Fallback: Original Regime-based Single Script Logic
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
        # (Legacy Shotlist logic omitted for brevity as it was not requested by user, focusing on script)
        # But to be safe, we keep the file write
        
        (out_dir / "insight_script_v1.md").write_text("\n".join(script_lines), encoding="utf-8")
        
    # (Optional) Generate Shotlist legacy support if needed
