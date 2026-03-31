# [PHASE-13] APPROVAL-FORENSICS SUMMARY REPORT
**분석 기간**: 최근 14일 (총 1124건 토픽 데이터 추출)
**목적**: 최종 승인(Complete) 건수가 0건으로 나오는 현상의 정량적 원인 규명 및 엔진 포착 능력 진단.

---

## 1. 정량적 분포 현황 (Complete 0건 분석)

*   **A. APPROVED 비율**: 0.00% (0 / 1124)
*   **B. video_ready True 비율**: 0.00% (0 / 1124)
*   **C. Intensity (강도)**: 평균 **38.43** / 중앙값 **6.00**
*   **D. Narrative Score (내러티브 점수)**: 평균 **0.13** / 중앙값 **0.00**
*   **E. Conflict Flag True 비율**: 0.00% (0 / 1124)
*   **F. Escalation Detected 비율**: 0.00% (0 / 1124)

---

## 2. Gate 컷 포인트 분석 (왜 탈락했는가?)

전체 실패 토픽들에 대해 컷오프(Cut-off) 원인을 분석한 결과입니다.

*   `CASE 1 (Intensity 부족)`: 684건
*   `CASE 2 (Narrative_Score 부족)`: 413건
*   `CASE 5 (Data_Incomplete)`: 27건
*   `CASE 3 (Actor_Tier 부족)`: 0건
*   `CASE 4 (Speakability 단계 컷)`: 0건
*   `CASE 6 (기타/알수없음)`: 0건

---

## 3. 경제사냥꾼(Economic Hunter) 재현 테스트 (최근 30일)
**테스트 조건**: Intensity >= 70 AND (Conflict OR Escalation) AND Narrative Score >= 70

*   **발굴된 잠재 영상형 후보 건수**: **0건** (별도 리스트: `economic_hunter_candidate_test.json` 저장 완료)
*   **영상화 가치 포착 능력 등급**: **D 등급**
*   **평가**: 엔진이 영상형 토픽을 전혀 포착하지 못하는 상태 (치명적 병목 지점 존재)

---

## 4. 최종 진단 및 결론

1.  **Complete 0건 현상의 정상성 여부**: **비정상 (Engine Blindness - 기초 체력 미달)**
    (엔진 초단의 원시 데이터 문제는 아닌지, 파이프라인 후단의 룰이 문제인지 입증하는 지표)
2.  **가장 큰 승인 실패 병목점**: 
    1순위: **CASE 1 (Intensity 부족)** 
    2순위: **CASE 2 (Narrative_Score 부족)**
3.  **현행 Gate 조건의 과도성 여부**: **원천 데이터 부족 (Source Drought)**

> **[조치 권고사항]**
> 본 분석은 코드(로직) 단의 어떠한 수정도 가하지 않았으며, 오직 데이터 메타데이터를 백트래킹한 결과입니다.
> 현재 나타난 병목 구간(1순위/2순위)의 Score 임계값을 하향하거나, Speakability 룰을 유연하게 조정하는 방향으로 Phase-14 튜닝을 검토해야 합니다.
