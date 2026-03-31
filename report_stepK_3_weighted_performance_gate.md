# 📜 [STEP-K-3] Weighted Performance Gate v1.0

## 1. 개요
본 단계에서는 엔진의 보정 승인 체계를 단순 "지표 하락 금지"에서 **"가중치 기반 성과 평가(Weighted Scoring)"**로 전환했습니다. 이를 통해 엔진이 상호 보충적인 지표들 사이에서 전략적인 트레이드오프(예: 구조적 일치도가 약간 낮아지더라도 수익률이 크게 개선되는 경우)를 수행하며 "수익 중심"으로 진화할 수 있도록 설계했습니다.

## 2. 주요 로직 및 가중치
### A. Metric Weights (가중치 정의)
수익성을 최우선으로 하되, 시스템 일관성을 유지할 수 있도록 가중치를 배분했습니다.
- **Avg Return (수익률)**: 0.5 (최우선)
- **Hit Ratio (적중률)**: 0.3
- **Alignment (구조 일치도)**: 0.2

### B. Weighted Score Calculation
보정 전/후의 지표 변화량(Delta)에 가중치를 곱해 합산합니다.
- `Score = (ΔReturn * 0.5) + (ΔHit * 0.3) + (ΔAlign * 0.2)`
- `Score > 0`인 경우에만 보정을 최종 승인(ACCEPT)합니다.

### C. Hard Constraints (절대 하한선)
전체 점수가 양수이더라도, 특정 지표의 파괴적인 하락을 방지하기 위해 절대 하한선을 적용합니다.
- **Avg Return**: -0.3 미만 하락 시 무조건 REJECT
- **Hit Ratio**: -0.2 미만 하락 시 무조건 REJECT

## 3. 검증 증거 (Verification Evidence)
### ✅ 테스트 케이스 1: 합리적 트레이드오프 승인
- **상황**: Alignment가 0.1 하락했으나, Avg Return이 0.2 상승함.
- **결과**: Weighted Score **+0.08** 산출 → `[SafetyGuard] ✅ ACCEPTED` 확인. 수익 중심의 진화가 정상 작동함을 증명했습니다.

### ✅ 테스트 케이스 2: 하한선 위반 차단
- **상황**: 다른 지표가 상승하더라도 Avg Return이 0.4 하락함.
- **결과**: `[SafetyGuard] 🚫 REJECTED: Hard Constraint Violation` 확인. 치명적인 성능 저하로부터 엔진을 보호합니다.

### ✅ 테스트 케이스 3: 음수 점수 거절
- **상황**: 지표들이 소폭 하락하여 전체 점수가 -0.045 산출됨.
- **결과**: `[SafetyGuard] ❌ REJECTED` 확인. 순손실이 발생하는 보정은 차단됩니다.

## 4. 로그 구조 업데이트
`data/ops/calibration_guard_log.json`에 각 지표별 기여도와 가중치가 적용된 상세 점수 내역이 기록됩니다.

---
**Status**: v1.0.0-PROFIT-ONLY-UPWARDS
