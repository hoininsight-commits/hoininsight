# [IS-111] Sector Rotation Acceleration Detector 가속 감지 레이어 완료

섹터 간 자금 이동이 단순한 로테이션을 넘어 **가속(Acceleration)** 단계에 진입했는지 결정론적으로 판정하는 레이어를 구현했습니다.

## 주요 변경 사항

### 1. 가속 판정 엔진 (Deterministic Engine)
- **[NEW] [sector_rotation_acceleration_detector.py](file:///Users/jihopa/.gemini/antigravity/scratch/HoinInsight/src/ui/sector_rotation_acceleration_detector.py)**
    - 3가지 조건(방향성 중첩, 성과 격차 확대, 내러티브 전환) 중 2개 이상 충족 시 `ACCELERATING` 판정.
    - 모든 판정 근거에 `(출처)`를 강제 포함하여 신뢰도 확보.

### 2. 경사 스타일 스크립트 자동 생성
- **[NEW] [sector_rotation_exporter.py](file:///Users/jihopa/.gemini/antigravity/scratch/HoinInsight/src/ui/sector_rotation_exporter.py)**
    - `exports/sector_rotation_long.txt`: 구조적 전환을 설명하는 롱폼 대본.
    - `exports/sector_rotation_shorts.txt`: "지금 들어가도 되나?"에 답하는 쇼츠 대본.

### 3. 검증 결과
- **[NEW] [verify_is111_sector_rotation.py](file:///Users/jihopa/.gemini/antigravity/scratch/HoinInsight/tests/verify_is111_sector_rotation.py)**
    - 5개 핵심 테스트 케이스 통과 (스키마, 출처 표기, undefined 체크 등).

## 증거 자료
- [IS-111 원격 검증 보고서](file:///Users/jihopa/.gemini/antigravity/scratch/HoinInsight/docs/engine/IS-111_REMOTE_VERIFICATION_REPORT.md)
- [생성된 가속 신호 JSON](file:///Users/jihopa/.gemini/antigravity/scratch/HoinInsight/data/ui/sector_rotation_acceleration.json)

## 향후 계획
- IS-112: Valuation Reset Detector 레이어 구현 예정.
