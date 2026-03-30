# 📜 [REPORT] STEP-H-CORE: Decision Timing & Impact Calibration v1.0

## 1. 개요 (Overview)
본 보고서는 STEP-H(Engine Validation Audit)에서 식별된 오차(Decision Timing 및 Stock Selection 분산)를 해결하기 위해 수행된 **Core Calibration**의 결과 및 검증 내용을 담고 있습니다.

## 2. 주요 개선 사항 (Key Calibrations)

### A. Timing Calibration
- **메커니즘**: Market Radar의 `evolution_stage`와 `momentum_score`를 결합한 결정론적 매핑 레이어를 도입했습니다.
- **결과**: `EXPANSION` 단계 및 `0.52` 모멘텀 발생 시, 감성적인 WATCH 판정을 배제하고 구조적인 **"ADD" (비중 확대)** 포지션을 정확하게 트리거합니다.

### B. Selection Calibration (Concentration)
- **메커니즘**: `selection_score` (Directness + Evidence Density) 기반의 Top-3 필터링을 강제했습니다.
- **결과**: 중구난방이던 종목 리스트를 고확신 종목(MSFT, NVDA, PLTR)으로 압축하여 성과 가독성을 높였습니다.

### C. Allocation Calibration (Structural Weighting)
- **메커니즘**: Recalibrated Confidence 수치를 `selection_score`와 직접 연계하여 가중치를 산출합니다.
- **결과**: 테마 직접도가 높고 증거가 풍부한 종목에 자원(Weight)을 집중 배치함으로써 Outcome Alignment를 개선했습니다.

## 3. 구조적 정합성 및 안정성 (System Stability)
- **Desynchronization 해결**: `data/operator/`와 `data/ops/` 간의 브리프 파일 불일치 문제를 해결하여, UI 배포 시 항상 보정된(Calibrated) 최신 데이터가 반영되도록 보장했습니다.
- **Type Safety 강화**: Recalibration 레이어에서 발생하는 타입 오류를 해결하여 파이프라인의 생존성을 확보했습니다.

## 4. 최종 검증 (Validation)
- **대상**: `2026-03-30` 파이프라인 실행 결과
- **판정**: **PASS**
    - Action: `ADD` (Calibrated)
    - Impact Chain: Top-3 Concentrated
    - Weight: Structural Adjustment Applied (MSFT 0.83, PLTR 0.51 등)
    - Persistence: `docs/data/ops/today_operator_brief.json`에 최종 반영 확인됨

---
**HOIN Insight Engine - STEP-H-CORE Verified State**
