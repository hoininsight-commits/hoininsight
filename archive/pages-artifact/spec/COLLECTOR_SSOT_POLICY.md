# Collector SSOT Policy

이 문서는 HOIN Insight 프로젝트의 데이터 수집기(Collector) 배치 및 관리 정책을 정의합니다.

## 1. 공식 수집기 경로 (Authorized Path)
**SSOT Path: src/engine/collectors/**

모든 신규 수집기는 위 경로에만 위치해야 합니다. 이는 엔진 코어 로직과 수집 로직을 물리적으로 통합하여 관리 효율성을 높이기 위함입니다.

## 2. 레거시 경로 (Deprecated Paths)
아래 경로는 더 이상 신규 수집기 추가를 허용하지 않습니다.
- `src/collectors/` (Deprecated)
- `src/events/collectors/` (Deprecated)

기존 파일은 유지되나, 신규 파일 추가 시 CI Guard에 의해 빌드가 차단됩니다.

## 3. 구현 원칙
- **추가 전용(Add-Only)**: 기존 수집 로직을 파괴하지 않고 추가합니다.
- **Shim 허용**: 레거시 경로에서 신규 경로의 수집기를 호출하는 Shim 구성은 과도기적으로 허용됩니다.
- **에러 핸들링**: 모든 수집기는 개별적으로 soft-fail 해야 하며, 전체 파이프라인을 중단시켜서는 안 됩니다.

## 4. CI Guard (Automated Enforcement)
`scripts/verify_collector_policy.py`가 아래 사항을 강제합니다.
- [FAIL] `src/collectors/` 또는 `src/events//` 내에 신규 파일 생성 시.
- [PASS] `src/engine/collectors/` 내에 파일 생성 시.
