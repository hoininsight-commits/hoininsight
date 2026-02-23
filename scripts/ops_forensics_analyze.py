#!/usr/bin/env python3
import json
import statistics
from pathlib import Path

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def write_md(path, content):
    Path(path).write_text(content, encoding="utf-8")

def main():
    print("Loading extracted forensics datasets...")
    data_14 = load_json("data_outputs/ops/approval_forensics_last14days.json")
    data_30 = load_json("data_outputs/ops/economic_hunter_candidates_30days.json")
    
    total_14 = len(data_14)
    if total_14 == 0:
        print("No topics found for last 14 days.")
        return

    # 1. Complete 0-case Quantitative Analysis
    approved_count = 0
    video_ready_count = 0
    intensities = []
    narrative_scores = []
    conflict_count = 0
    escalation_count = 0

    # 2. Gate Cut Point Forensics
    cut_counts = {
        "CASE 1 (Intensity 부족)": 0,
        "CASE 2 (Narrative_Score 부족)": 0,
        "CASE 3 (Actor_Tier 부족)": 0,
        "CASE 4 (Speakability 단계 컷)": 0,
        "CASE 5 (Data_Incomplete)": 0,
        "CASE 6 (기타/알수없음)": 0
    }

    for t in data_14:
        # A. APPROVED
        if t['status'] == 'APPROVED' or t['status'] == 'COMPLETE':
            approved_count += 1
            
        # B. video_ready
        if t['video_ready'] is True or str(t['video_ready']).lower() == 'true':
            video_ready_count += 1
            
        # C, D. intensity / narrative_score
        try:
            val_int = float(t['intensity'])
            intensities.append(val_int)
        except (ValueError, TypeError):
            intensities.append(0.0)
            
        try:
            val_nar = float(t['narrative_score'])
            narrative_scores.append(val_nar)
        except (ValueError, TypeError):
            narrative_scores.append(0.0)
            
        # E, F. boolean flags
        if t['conflict_flag'] is True or str(t['conflict_flag']).lower() == 'true':
            conflict_count += 1
        if t['escalation_detected'] is True or str(t['escalation_detected']).lower() == 'true':
            escalation_count += 1

        # Gate Forensics (Only for non-approved)
        if t['status'] not in ['APPROVED', 'COMPLETE']:
            int_val = intensities[-1]
            nar_val = narrative_scores[-1]
            actor_val = 0
            try:
                actor_val = float(t['structural_actor_score'])
            except:
                pass
                
            speak = str(t['speakability']).upper()
            
            if int_val == 0 and nar_val == 0 and actor_val == 0:
                cut_counts["CASE 5 (Data_Incomplete)"] += 1
            elif int_val < 50:
                cut_counts["CASE 1 (Intensity 부족)"] += 1
            elif nar_val < 60:
                cut_counts["CASE 2 (Narrative_Score 부족)"] += 1
            elif actor_val < 40:
                cut_counts["CASE 3 (Actor_Tier 부족)"] += 1
            elif speak not in ['READY', 'APPROVED']:
                cut_counts["CASE 4 (Speakability 단계 컷)"] += 1
            else:
                cut_counts["CASE 6 (기타/알수없음)"] += 1

    approved_pct = (approved_count / total_14) * 100
    video_ready_pct = (video_ready_count / total_14) * 100
    conflict_pct = (conflict_count / total_14) * 100
    escalation_pct = (escalation_count / total_14) * 100
    
    int_avg = sum(intensities) / total_14
    int_med = statistics.median(intensities)
    nar_avg = sum(narrative_scores) / total_14
    nar_med = statistics.median(narrative_scores)

    # 3. Economic Hunter Reproduction Test (30 days)
    hunter_candidates = []
    for t in data_30:
        try:
            i_val = float(t['intensity'])
            n_val = float(t['narrative_score'])
        except:
            continue
            
        cf = t['conflict_flag'] in [True, 'true', 'True']
        ed = t['escalation_detected'] in [True, 'true', 'True']
        
        if i_val >= 70 and (cf or ed) and n_val >= 70:
            hunter_candidates.append(t)
            
    write_json("data_outputs/ops/economic_hunter_candidate_test.json", hunter_candidates)
    
    hunter_count = len(hunter_candidates)
    hunter_eval = ""
    if hunter_count == 0:
        hunter_eval = "엔진이 영상형 토픽을 전혀 포착하지 못하는 상태 (치명적 병목 지점 존재)"
        grade = "D 등급"
    elif hunter_count < 5:
        hunter_eval = "엔진이 가끔 영상형 토픽의 잠재력을 포착하지만 수율이 극단적으로 낮음"
        grade = "C 등급"
    elif hunter_count < 15:
        hunter_eval = "주 2-3회 정도의 영상화 가치 토픽을 포착해내는 양호한 풀을 소유하고 있음"
        grade = "B 등급"
    else:
        hunter_eval = "매우 강력한 영상화 가치 토픽 포착 능력을 지니고 있으며, 단순히 후단 Gate에서 막혀있음"
        grade = "A 등급"

    # Determine Bottleneck
    bottleneck_ranking = sorted(cut_counts.items(), key=lambda x: x[1], reverse=True)
    b1 = bottleneck_ranking[0][0]
    b2 = bottleneck_ranking[1][0] if len(bottleneck_ranking) > 1 else "None"
    
    is_normal = "비정상 (Abnormal)" if approved_pct == 0 and hunter_count > 0 else "정상 (Normal Data Drought)"
    if approved_pct == 0 and hunter_count == 0:
        is_normal = "비정상 (Engine Blindness - 기초 체력 미달)"

    gate_strictness = "과도함 (Too Strict)" if cut_counts["CASE 4 (Speakability 단계 컷)"] > total_14 * 0.4 else "적정함 (Moderate)"
    if cut_counts["CASE 1 (Intensity 부족)"] > total_14 * 0.5:
        gate_strictness = "원천 데이터 부족 (Source Drought)"

    # Markdown Report Generation
    md_content = f"""# [PHASE-13] APPROVAL-FORENSICS SUMMARY REPORT
**분석 기간**: 최근 14일 (총 {total_14}건 토픽 데이터 추출)
**목적**: 최종 승인(Complete) 건수가 0건으로 나오는 현상의 정량적 원인 규명 및 엔진 포착 능력 진단.

---

## 1. 정량적 분포 현황 (Complete 0건 분석)

*   **A. APPROVED 비율**: {approved_pct:.2f}% ({approved_count} / {total_14})
*   **B. video_ready True 비율**: {video_ready_pct:.2f}% ({video_ready_count} / {total_14})
*   **C. Intensity (강도)**: 평균 **{int_avg:.2f}** / 중앙값 **{int_med:.2f}**
*   **D. Narrative Score (내러티브 점수)**: 평균 **{nar_avg:.2f}** / 중앙값 **{nar_med:.2f}**
*   **E. Conflict Flag True 비율**: {conflict_pct:.2f}% ({conflict_count} / {total_14})
*   **F. Escalation Detected 비율**: {escalation_pct:.2f}% ({escalation_count} / {total_14})

---

## 2. Gate 컷 포인트 분석 (왜 탈락했는가?)

전체 실패 토픽들에 대해 컷오프(Cut-off) 원인을 분석한 결과입니다.

*   `{bottleneck_ranking[0][0]}`: {bottleneck_ranking[0][1]}건
*   `{bottleneck_ranking[1][0]}`: {bottleneck_ranking[1][1]}건
*   `{bottleneck_ranking[2][0]}`: {bottleneck_ranking[2][1]}건
*   `{bottleneck_ranking[3][0]}`: {bottleneck_ranking[3][1]}건
*   `{bottleneck_ranking[4][0]}`: {bottleneck_ranking[4][1]}건
*   `{bottleneck_ranking[5][0]}`: {bottleneck_ranking[5][1]}건

---

## 3. 경제사냥꾼(Economic Hunter) 재현 테스트 (최근 30일)
**테스트 조건**: Intensity >= 70 AND (Conflict OR Escalation) AND Narrative Score >= 70

*   **발굴된 잠재 영상형 후보 건수**: **{hunter_count}건** (별도 리스트: `economic_hunter_candidate_test.json` 저장 완료)
*   **영상화 가치 포착 능력 등급**: **{grade}**
*   **평가**: {hunter_eval}

---

## 4. 최종 진단 및 결론

1.  **Complete 0건 현상의 정상성 여부**: **{is_normal}**
    (엔진 초단의 원시 데이터 문제는 아닌지, 파이프라인 후단의 룰이 문제인지 입증하는 지표)
2.  **가장 큰 승인 실패 병목점**: 
    1순위: **{b1}** 
    2순위: **{b2}**
3.  **현행 Gate 조건의 과도성 여부**: **{gate_strictness}**

> **[조치 권고사항]**
> 본 분석은 코드(로직) 단의 어떠한 수정도 가하지 않았으며, 오직 데이터 메타데이터를 백트래킹한 결과입니다.
> 현재 나타난 병목 구간(1순위/2순위)의 Score 임계값을 하향하거나, Speakability 룰을 유연하게 조정하는 방향으로 Phase-14 튜닝을 검토해야 합니다.
"""
    write_md("data_outputs/ops/approval_forensics_summary.md", md_content)
    print("Report generated: data_outputs/ops/approval_forensics_summary.md")

if __name__ == "__main__":
    main()
