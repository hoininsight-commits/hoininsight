#!/usr/bin/env python3
import json
import statistics
from pathlib import Path

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write_md(path, content):
    Path(path).write_text(content, encoding="utf-8")

def analyze_components(data):
    fields = [
        'intensity', 'narrative_score', 'actor_tier_score', 
        'capital_flow_score', 'policy_score', 'persistence_score', 
        'cross_axis_count', 'cross_axis_multiplier'
    ]
    
    stats = {}
    for f in fields:
        vals = []
        zero_count = 0
        for t in data:
            try:
                v = float(t.get(f, 0))
            except:
                v = 0.0
            vals.append(v)
            if v == 0:
                zero_count += 1
                
        vals.sort(reverse=True)
        stats[f] = {
            'avg': sum(vals) / max(len(vals), 1),
            'med': statistics.median(vals) if vals else 0,
            'zero_pct': (zero_count / max(len(vals), 1)) * 100,
            'nz_pct': ((len(vals) - zero_count) / max(len(vals), 1)) * 100,
            'top10': vals[:10]
        }
        
    return stats

def analyze_flags(data):
    flags = ['escalation_detected', 'conflict_flag']
    counts = {f: 0 for f in flags}
    total = len(data)
    
    for t in data:
        for f in flags:
            val = t.get(f)
            if val is True or str(val).lower() == 'true':
                counts[f] += 1
                
    return counts, total

def main():
    data = load_json("data_outputs/ops/narrative_component_autopsy_last14days.json")
    total = len(data)
    if total == 0:
        print("No data extracted.")
        return

    # 1. Component distribution
    stats = analyze_components(data)
    flags, _ = analyze_flags(data)

    # 2. Stage Failure Map
    stage_fails = {
        'Step 1 (Intensity < 50)': 0,
        'Step 2 (Actor Score == 0)': 0,
        'Step 3 (Flow/Policy/Persistence All == 0)': 0,
        'Step 4 (No Cross Axis Triggered)': 0,
        'Step 5 (No Escalation Triggered)': 0
    }
    
    for t in data:
        try:
            i_val = float(t.get('intensity', 0))
            actor = float(t.get('actor_tier_score', 0))
            flow = float(t.get('capital_flow_score', 0))
            pol = float(t.get('policy_score', 0))
            pers = float(t.get('persistence_score', 0))
            cross = float(t.get('cross_axis_multiplier', 0))
        except:
            i_val, actor, flow, pol, pers, cross = 0, 0, 0, 0, 0, 0
            
        esc = t.get('escalation_detected') in [True, 'true', 'True']
        
        if i_val < 50:
            stage_fails['Step 1 (Intensity < 50)'] += 1
        if actor == 0:
            stage_fails['Step 2 (Actor Score == 0)'] += 1
        if flow == 0 and pol == 0 and pers == 0:
            stage_fails['Step 3 (Flow/Policy/Persistence All == 0)'] += 1
        if cross <= 1.0:
            stage_fails['Step 4 (No Cross Axis Triggered)'] += 1
        if not esc:
            stage_fails['Step 5 (No Escalation Triggered)'] += 1

    # 3. Root Cause Classification for 0-Score
    zero_score_causes = {
        'CASE A (Actor Score == 0)': 0,
        'CASE B (All Structural Scores == 0)': 0,
        'CASE C (Intensity < 50)': 0,
        'CASE D (Cross Axis == 0)': 0,
        'CASE E (Missing Fields / None)': 0,
        'CASE F (Other)': 0
    }
    
    zero_score_topics = 0
    missing_invocation = 0
    
    for t in data:
        nar_score = 0
        try:
            nar_score = float(t.get('narrative_score', 0))
        except:
            pass
            
        if not t.get('_has_narrative_score', False):
            missing_invocation += 1
            
        if nar_score == 0:
            zero_score_topics += 1
            
            try:
                actor = float(t.get('actor_tier_score', 0))
                flow = float(t.get('capital_flow_score', 0))
                pol = float(t.get('policy_score', 0))
                pers = float(t.get('persistence_score', 0))
                cross = float(t.get('cross_axis_multiplier', 0))
                i_val = float(t.get('intensity', 0))
            except:
                actor, flow, pol, pers, cross, i_val = 0, 0, 0, 0, 0, 0
                
            if not t.get('_has_narrative_score', False):
                zero_score_causes['CASE E (Missing Fields / None)'] += 1
            elif actor == 0:
                zero_score_causes['CASE A (Actor Score == 0)'] += 1
            elif flow == 0 and pol == 0 and pers == 0:
                zero_score_causes['CASE B (All Structural Scores == 0)'] += 1
            elif i_val < 50:
                zero_score_causes['CASE C (Intensity < 50)'] += 1
            elif cross <= 1.0:
                zero_score_causes['CASE D (Cross Axis == 0)'] += 1
            else:
                zero_score_causes['CASE F (Other)'] += 1

    missing_pct = (missing_invocation / total) * 100
    zero_pct_overall = (zero_score_topics / total) * 100

    # Determine core evaluation
    conclusion1 = "계산 로직 자체가 누락됨 (CASE E 지배적)" if missing_pct > 50 else ("입력 조건(데이터/Intensity)이 충족되지 않음" if stage_fails['Step 1 (Intensity < 50)'] > total * 0.5 else "구조축 점수 획득 실패 (CASE A/B 지배적)")
    conclusion2 = "정상 발동됨" if missing_pct < 10 else "호출 누락 빈도 높음"
    conclusion3 = "현실 반영 미흡 (모든 구조축 점수가 0에 수렴하는 극단적 보수성 표출)" if stats['actor_tier_score']['zero_pct'] > 80 else "정상 범주"

    # Markdown - Distribution
    md_dist = f"""# [PHASE-14A] NARRATIVE COMPONENT DISTRIBUTION REPORT
**분석 기간**: 최근 14일 (총 {total}건 토픽 데이터 추출)
**목적**: Narrative Score 0점 수렴의 구성요소별 정밀 해부분석.

---

## 1. 구성요소별 통계 분포

| 구성요소 | 평균 | 중앙값 | 0값 비율(%) | Non-zero 비율(%) | 상위 10개 샘플 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Actor Tier Score** | {stats['actor_tier_score']['avg']:.2f} | {stats['actor_tier_score']['med']:.2f} | {stats['actor_tier_score']['zero_pct']:.1f}% | {stats['actor_tier_score']['nz_pct']:.1f}% | {stats['actor_tier_score']['top10'][:5]}... |
| **Capital Flow Score** | {stats['capital_flow_score']['avg']:.2f} | {stats['capital_flow_score']['med']:.2f} | {stats['capital_flow_score']['zero_pct']:.1f}% | {stats['capital_flow_score']['nz_pct']:.1f}% | {stats['capital_flow_score']['top10'][:5]}... |
| **Policy Score** | {stats['policy_score']['avg']:.2f} | {stats['policy_score']['med']:.2f} | {stats['policy_score']['zero_pct']:.1f}% | {stats['policy_score']['nz_pct']:.1f}% | {stats['policy_score']['top10'][:5]}... |
| **Persistence Score**| {stats['persistence_score']['avg']:.2f} | {stats['persistence_score']['med']:.2f} | {stats['persistence_score']['zero_pct']:.1f}% | {stats['persistence_score']['nz_pct']:.1f}% | {stats['persistence_score']['top10'][:5]}... |
| **Narrative Score** | {stats['narrative_score']['avg']:.2f} | {stats['narrative_score']['med']:.2f} | {stats['narrative_score']['zero_pct']:.1f}% | {stats['narrative_score']['nz_pct']:.1f}% | {stats['narrative_score']['top10'][:5]}... |

*   **Cross Axis Multiplier 발동 횟수 (> 1.0)**: {total - int(stage_fails['Step 4 (No Cross Axis Triggered)'])} 회 발동
*   **Escalation Detected True 횟수**: {flags['escalation_detected']} 회 발동
*   **Conflict Flag True 횟수**: {flags['conflict_flag']} 회 발동

---

## 2. 점수 계산 0점 원인 (Root Cause Classification)
총 {zero_score_topics}건의 Narrative Score === 0 토픽을 분해한 결과입니다.

*   `CASE A (Actor Score == 0)`: {zero_score_causes['CASE A (Actor Score == 0)']}건
*   `CASE B (All Structural Scores == 0)`: {zero_score_causes['CASE B (All Structural Scores == 0)']}건
*   `CASE C (Intensity < 50)`: {zero_score_causes['CASE C (Intensity < 50)']}건
*   `CASE E (Missing Fields / None)`: {zero_score_causes['CASE E (Missing Fields / None)']}건
    -> 전체 {total}건 중 `narrative_score` 호출/세팅 누락 빈도: {missing_pct:.1f}%

---

## 3. 최종 진단 결론
① **계산 로직은 정상이나 입력 조건이 충족되지 않는 상태인가?**: {conclusion1}
② **계산 로직이 사실상 발동하지 않는 상태인가?**: {conclusion2}
③ **구조적 신호 감지 알고리즘이 현실을 반영하지 못하는가?**: {conclusion3}

> **[조치 권고사항]**
> Actor Score 와 Flow/Policy Score 의 산출 방식이 비정상적으로 억제되어 있습니다. Component 의 가중치가 아니라, 엔진이 **구조적 액터를 인지하는 기준(Dictionary 또는 Regex 매칭률)** 자체가 완전히 망가져 있을 확률이 유력합니다.
"""
    write_md("data_outputs/ops/narrative_component_distribution.md", md_dist)
    print("Report generated: data_outputs/ops/narrative_component_distribution.md")

    # Markdown - Stage Map
    md_stage = f"""# [PHASE-14A] NARRATIVE STAGE FAILURE MAP
**분석 기간**: 최근 14일 (총 {total}건)

점수 계산에 이르는 5단계의 통과 여부를 검증한 시뮬레이션입니다. 아래 항목에서 각 단계별 '비통과율(Fail Rate)'을 추적합니다.

*   **Step 1. Intensity Pass (< 50)**
    탈락: {stage_fails['Step 1 (Intensity < 50)']}건 ({(stage_fails['Step 1 (Intensity < 50)']/total)*100:.1f}%)
    
*   **Step 2. Actor Score Pass (== 0)**
    탈락: {stage_fails['Step 2 (Actor Score == 0)']}건 ({(stage_fails['Step 2 (Actor Score == 0)']/total)*100:.1f}%)

*   **Step 3. Structural Subs Pass (Flow/Policy/Persist All == 0)**
    탈락: {stage_fails['Step 3 (Flow/Policy/Persistence All == 0)']}건 ({(stage_fails['Step 3 (Flow/Policy/Persistence All == 0)']/total)*100:.1f}%)

*   **Step 4. Cross Axis Triggered (<= 1.0)**
    탈락: {stage_fails['Step 4 (No Cross Axis Triggered)']}건 ({(stage_fails['Step 4 (No Cross Axis Triggered)']/total)*100:.1f}%)

*   **Step 5. Escalation Triggered (False)**
    탈락: {stage_fails['Step 5 (No Escalation Triggered)']}건 ({(stage_fails['Step 5 (No Escalation Triggered)']/total)*100:.1f}%)
"""
    write_md("data_outputs/ops/narrative_stage_failure_map.md", md_stage)
    print("Report generated: data_outputs/ops/narrative_stage_failure_map.md")


if __name__ == "__main__":
    main()
