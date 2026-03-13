# IS-44: Topic-Centric Operational Dashboard Specification

## 1. Overview
The Operational Dashboard is a human-centric tool designed for editorial meetings. It suppresses technical engine logs in favor of decision-ready topic summaries and execution packages.

## 2. Core Screen Structure

### 2.1 TOPIC BOARD (Main View)
- **Target**: Only show today's selected topics (Processed Topics).
- **Card Elements (KR Only)**:
  - **제목**: 토픽 한 문장 제목.
  - **상태**: 발화 확정 (ACTIVE), 보류 (HOLD), 침묵 (SILENT).
  - **출력 형식**: 대형 영상, 숏츠, 텍스트.
  - **판단 요약**: "지금 말하는 이유" 또는 "침묵 사유".

### 2.2 TOPIC DETAIL (Expanded View)
1. **토픽 요약**: 선정 배경, 시장 표면 해석 vs IS 해석.
2. **판단 근거**: HoinEngine 요약, 공식 인용문/출처, 검증 상태.
3. **자본 경로**: 병목 지점, 티커, 킬 스위치.
4. **콘텐츠 패키지**: 롱폼, 숏츠(3종), 텍스트 카드.
5. **사후 판단**: 과거 유사 사례 성과.

## 3. Localization Rules
- **No English visible** on the main operational UI.
- Mapping:
  - ACTIVE -> **발화 확정**
  - HOLD -> **보류**
  - SILENT -> **침묵**
  - OUTPUT -> **출력 형식**
  - URGENCY -> **발화 압력**

## 4. Implementation Strategy
- Modify `DecisionDashboard` to generate a primary `operational_view.md`.
- Keep the existing `decision_dashboard.md` as the "Developer/Verification" view.
- Update `run_topic_gate.py` to trigger both or prioritize the operational view.
