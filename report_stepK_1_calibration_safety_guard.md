# 📜 [STEP-K-1] Calibration Safety Guard v1.0

## 1. 개요
본 단계에서는 엔진의 자율적인 진화 과정에서 발생할 수 있는 파라미터 폭주, 중복 적용, 성과 퇴보 등의 리스크를 차단하기 위한 **안전 레이어**를 구축했습니다. 이제 모든 보정(Calibration) 실행은 사전에 정의된 물리적 한계 내에서만 허용되며, 실행 전 스냅샷 생성 및 성과 검증을 통한 자동 롤백 기능을 지원합니다.

## 2. 적용된 Safety Guards
### A. Parameter Boundary Enforcement (파라미터 상한/하한 제한)
엔진 파라미터가 비정상적인 범위로 발산하는 것을 방지합니다.
- **solver_pool_size**: 3 ~ 10 (종목 풀 크기 제한)
- **solver_weight**: 0.5 ~ 2.0 (솔버 영향력 제한)
- **demand_weight**: 0.3 ~ 1.5 (수요 데이터 가중치 제한)
- **timing_threshold**: 0.2 ~ 0.8 (타이밍 민감도 제한)

### B. Duplicate Action Prevention (중복 적용 방지)
최근 5건의 실행 로그를 분석하여 동일한 대상(`target`)에 대해 동일한 액션(`action`)이 반복 적용되는 것을 차단합니다. 이를 통해 보정의 과도한 누적을 방지합니다.

### C. Snapshot & Rollback (스냅샷 및 롤백)
- **Before-Execution Snapshot**: 보정 실행 직전의 파라미터 상태를 `data/ops/calibration_snapshot.json`에 저장합니다.
- **Auto-Rollback**: 보정 적용 후 성과 지표(Alignment)가 이전보다 하락할 경우, 즉시 스냅샷을 사용하여 엔진 파라미터를 복구합니다.

### D. Performance Verification Gate (성과 검증 게이트)
- 보정 전 지표와 보정 후 예상 지표를 비교하여 `ACCEPT` 또는 `REJECT`를 결정합니다.
- `REJECT` 시 해당 세션의 모든 파라미터 변경은 무효화됩니다.

## 3. 검증 증거 (Verification Evidence)
### ✅ 테스트 케이스 1: 중복 차단
- `EXPAND_SOLVER_POOL` 액션이 로그에 이미 있는 경우, 추가 실행 시 `[Calibration-Guard] 🛡️ Duplicate Action Blocked` 로그와 함께 무시됨을 확인했습니다.

### ✅ 테스트 케이스 2: 상한선 제한 (Clipping)
- `solver_pool_size`를 15로 업데이트 시도 시, 설정된 Max값인 **10**으로 강제 조정(Clipped)됨을 확인했습니다.

### ✅ 테스트 케이스 3: 롤백 기능
- 임의로 성과 지표 하락(0.8 -> 0.5)을 발생시켰을 때, `[SafetyGuard] 🔄 Rollback executed` 메시지와 함께 파마미터가 보정 전 상태로 복구됨을 확인했습니다.

## 4. 생성된 데이터 파일
- `data/ops/calibration_guard_log.json`: 안전장치 작동 이력 및 성과 비교 로그
- `data/ops/calibration_snapshot.json`: 최신 롤백용 스냅샷 데이터

---
**Status**: v1.0.0-READY-FOR-SAFE-EVOLUTION
