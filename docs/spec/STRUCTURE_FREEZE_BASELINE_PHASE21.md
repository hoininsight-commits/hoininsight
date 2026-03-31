# Structure Freeze Baseline (Phase 21)

본 문서는 Phase 21 에이전트 모듈화가 완료된 시점의 시스템 구조를 동결(Freeze)하기 위한 기준 원장입니다. 이 문서에 명시되지 않은 구조적 변경은 금지되며, 변경 시 반드시 가드 통과 및 문서 갱신이 필요합니다.

## 1. 런타임 엔트리포인트 (Agents)
아래 6개 에이전트는 프로젝트 실행의 최상위 인터페이스로 고정됩니다.

- **A1**: `src.agents.data_agent`
- **A2**: `src.agents.signal_agent`
- **A3**: `src.agents.narrative_agent`
- **A4**: `src.agents.decision_agent`
- **A5**: `src.agents.video_agent`
- **A6**: `src.agents.publish_agent` (SSOT Shim)
- **SSOT Publisher**: `src.ui.run_publish_ui_decision_assets` (Implementation)

## 2. 핵심 데이터 산출물 경로 (Core Artifacts)
- **Local Source**:
  - `data/topics/candidates/{YYYY}/{MM}/{DD}/topic_candidates.json`
  - `data/decision/{YYYY}/{MM}/{DD}/final_decision_card.json`
- **Publish Destination (docs/)**:
  - `docs/data/decision/manifest.json`
  - `docs/data/decision/today.json`
  - `docs/data/video/video_candidate_pool.json`

## 3. 원격 검증 엔드포인트 (Remote Endpoints)
- **Manifest**: `https://hoininsight-commits.github.io/hoininsight/data/decision/manifest.json`
- **Today**: `https://hoininsight-commits.github.io/hoininsight/data/decision/today.json`
- **Video Pool**: `https://hoininsight-commits.github.io/hoininsight/data/video/video_candidate_pool.json`

## 4. 활성 CI 가드 목록 (CI Guards)
- **`verify_no_duplicate_publishers.py`**: 배포 로직 중복 방지.
- **`verify_agent_contracts.py`**: 에이전트 산출물 규격 검증.
- **`verify_no_cross_layer_imports.py`**: 계층 간 독립성 유지.
- **`verify_release_integrity.py`**: 배포 자산 무결성 및 누락 확인.
- **`verify_no_scoring_leak.py`**: 발행 단계의 스코어 계산 금지.

## 5. 구조 동결 선언 (Freeze Declaration)
> **[NOTICE]** 본 Baseline에 정의된 구조적 인터페이스 및 데이터 경로는 Phase 21의 표준입니다. 어떠한 신규 기능 추가도 본 구조를 훼손하거나 에이전트 필드 계약을 위반해서는 안 됩니다.

**Status**: ❄️ Frozen (Phase 21 Baseline)
**Date**: 2026-03-03
