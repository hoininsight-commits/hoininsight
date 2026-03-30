# 📜 [STEP-K-2] Multi-Metric Safety Guard v1.0

## 1. 개요
본 단계에서는 엔진의 보정 승인 로직을 단일 지표(Alignment)에서 다중 지표(Multi-Metric) 체계로 확장했습니다. 또한, 엔진의 상태를 이력으로 관리(Snapshot History)하고, 역대 최상의 성능을 보여준 상태를 별도로 보존(Best State)함으로써 엔진이 항상 "최적의 방향"으로만 진화하도록 강제합니다.

## 2. 주요 변경 사항
### A. Multi-Metric 검증 로직 도입
단일 지표의 왜곡을 방지하기 위해 다음 3가지 지표를 동시에 평가합니다:
- **Alignment**: 엔진 판단과 실제 결과의 구조적 일치도
- **Hit Ratio**: 추천 종목의 상승/하락 적중률
- **Avg Return**: Top 3 종목의 평균 수익률
> 보정 후 위 지표 중 하나라도 하락할 경우, 해당 보정은 즉시 거절(REJECT)되고 롤백됩니다.

### B. Snapshot History (최대 10개)
- `data/ops/calibration_snapshot_history.json`
- 모든 보정 실행 전의 상태를 파라미터와 메트릭을 포함하여 저장합니다.
- 최대 10개의 최신 이력을 유지하여 운영자가 언제든 과거 상태로 복구할 수 있는 기반을 마련했습니다.

### C. Best State Management
- `data/ops/calibration_best_state.json`
- `Avg Return`을 제1기준으로, `Hit Ratio`를 제2기준으로 하여 역대 최고의 성능을 기록한 파라미터 셋을 별도로 저장합니다.
- 현재 상태가 Best State보다 우수할 경우에만 자동으로 업데이트됩니다.

## 3. 검증 증거 (Verification Evidence)
### ✅ 테스트 케이스 1: 다중 지표 거절
- `Avg Return`이 하락(1.5 -> 1.2)하는 시나리오에서 `[SafetyGuard] ❌ Rejected: AVG_RETURN_DOWN` 메시지와 함께 보정이 차단됨을 확인했습니다.

### ✅ 테스트 케이스 2: 이력 관리 및 순환
- 3회의 보정 시도 후 `snapshot_history.json`에 3개의 독립적인 상태가 타임스탬프와 함께 기록됨을 확인했습니다.

### ✅ 테스트 케이스 3: Best State 업데이트
- 더 높은 수익률(2.5)을 가진 스냅샷이 입력될 때 `🏆 NEW BEST STATE RECORDED` 로그와 함께 파일이 갱신됨을 확인했습니다.

## 4. 생성된 데이터 파일
- `data/ops/calibration_snapshot_history.json`: 최근 10개 상태 이력
- `data/ops/calibration_best_state.json`: 역대 최상 성능 상태

---
**Status**: v1.0.0-EVOLUTION-ONLY-UPWARDS
