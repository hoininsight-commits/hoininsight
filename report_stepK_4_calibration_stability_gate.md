# 📜 [STEP-K-4] Calibration Stability Gate v1.0

## 1. 개요
본 단계에서는 엔진의 진화 과정에서 발생하는 미세한 노이즈(Noise)를 제거하고, 파라미터가 과도하게 흔들리는 현상(Drift)을 방지하기 위한 **"안정성 게이트(Stability Gate)"**를 도입했습니다. 이를 통해 엔진은 의미 있는 수준의 성과 개선이 확인될 때만 선택적으로 변화를 수용하며, 연속적인 보정 후에는 반드시 냉각기(Cooldown)를 거치도록 강제됩니다.

## 2. 주요 안정성 규칙
### A. Noise Filter (미세 변동 제거)
- **임계값**: `MIN_DELTA = 0.01` (1%)
- 모든 지표의 변화량이 1% 미만일 경우, 통계적으로 유의미하지 않은 노이즈로 간주하여 보정을 차단합니다. (`REJECT_NOISE`)

### B. Minimum Score Threshold (최소 개선 폭)
- **임계값**: `MIN_SCORE_THRESHOLD = 0.05`
- 가중 점수(Weighted Score)가 0.05 미만인 경우, 개선 효과가 투입 리스크 대비 낮다고 판단하여 보정을 거절합니다. (`REJECT_LOW_SCORE`)

### C. Cooldown System (진화 냉각기)
- **규칙**: `MAX_CONSECUTIVE_CALIBRATION = 3`
- 최근 3회 연속으로 보정이 승인된 경우, 시스템 안정화를 위해 다음 2회(COOLDOWN_PERIOD) 동안은 성과와 관계없이 보정을 제한합니다. (`REJECT_COOLDOWN`)

## 3. 검증 증거 (Verification Evidence)
### ✅ 테스트 케이스 1: 노이즈 차단
- **상황**: 지표 변화량이 0.005(0.5%)인 경우.
- **결과**: `[SafetyGuard] ⚠️ REJECTED: NOISE` 확인. 무의미한 파라미터 변경을 방지함.

### ✅ 테스트 케이스 2: 낮은 점수 차단
- **상황**: 가중 점수가 0.03으로 산출된 경우.
- **결과**: `[SafetyGuard] ⚠️ REJECTED: LOW_SCORE` 확인. 확실한 개선이 있을 때만 진화함.

### ✅ 테스트 케이스 3: 연속 보정 후 쿨다운
- **상황**: 최근 3회 연속 `ACCEPT` 로그가 존재하는 상태에서 보정 시도.
- **결과**: `[SafetyGuard] 🧊 REJECTED: COOLDOWN` 확인. 시스템의 과도한 변동성을 억제함.

## 4. 로그 확장
`data/ops/calibration_guard_log.json`에 `reason` 필드가 추가되어, 안정성 게이트에 의해 차단된 이유(NOISE, LOW_SCORE, COOLDOWN)가 명확히 기록됩니다.

---
**Status**: v1.0.0-STEADY-EVOLUTION
