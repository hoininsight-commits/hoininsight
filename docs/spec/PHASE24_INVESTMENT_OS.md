# PHASE 24: Structural Investment OS Layer v1.0

## 1. 개요 (Overview)
Phase 24는 이전 레이어들의 산출물(Regime, Conflict Density, Stock Linkage, Decision)을 결합하여, 운영자가 즉각적으로 현 상황을 진단하고 대응 우선순위를 결정할 수 있게 돕는 **"Structural Investment OS Layer"**입니다.

## 2. 설계 원칙 (Design Principles)
- **No-Behavior-Change**: 엔진의 점수 계산이나 승인 로직에 개입하지 않습니다.
- **No-Scoring-Leak**: UI나 OS 레이어에서 가짜 점수를 생성하지 않습니다.
- **Classification vs Prediction**: 단순 매수/매도 예측이 아닌, 상황의 정합성에 기반한 "분류(OPPORTUNITY, RISK, MONITOR)"를 제공합니다.
- **Layer Isolation**: `NarrativeAgent`의 마지막 단계로 추가되어 기존 엔진 로직과 격리됩니다.

## 3. 입력 및 출력 (I/O)
- **입력**: 
  - `regime_state.json` (Phase 23)
  - `conflict_density_pack.json` (Phase 22C)
  - `stock_linkage_pack.json` (Phase 22B)
  - `today.json` / `final_decision_card.json` (Decision)
- **출력**:
  - `data_outputs/ops/investment_os_state.json` (Structured JSON)
  - `data_outputs/ops/investment_os_brief.md` (Markdown summary)

## 4. OS 분류 규칙 (Classification Rules)
- **OPPORTUNITY**: Regime 핵심 축과 Topic Axis가 일치하며, 영상 후보군 또는 높은 Narrative 점수를 보유한 경우.
- **RISK**: Regime 리스크 축과 Axis가 일치하며, Conflict Density가 높거나 Risk Note가 존재하는 경우.
- **MONITOR**: 기타 모든 유효 신호. 축 정합성이 낮거나 데이터가 부족한 경우.

## 5. UI 통합 계획
- **전용 동선**: `#os` 라우트 또는 운영 대시보드 전용 섹션.
- **화면 구성**:
  - **Top**: Regime 요약 및 OS Stance (DEFENSIVE / NEUTRAL / RISK-ON).
  - **Middle**: 관찰 체크리스트 및 금지 사항 (Do-not-do).
  - **Bottom**: 선정된 Priority Topics 카드 (이유, 연결 종목, 체크리스트 포함).

## 6. 검증 계획
- **CI Guard**: `investment_os_state.json` 내 필수 필드(regime.state, os_summary.stance 등) 존재 여부 체크.
- **Remote Verification**: GitHub Pages 배포 후 JSON/MD 엔드포인트 200 OK 확인.
