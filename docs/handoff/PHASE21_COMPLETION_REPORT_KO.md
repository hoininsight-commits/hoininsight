# Phase 21: Agent Modularization Completion Report

Phase 21에서는 프로젝트의 런타임 구조를 6개의 독립적인 **Agent** 모듈로 재정의하고 엔트리포인트를 표준화했습니다. 이를 통해 로직의 변경 없이도 관리 효율성과 확장성을 극대화했습니다.

## 1. 구현된 Agent 모델 (A1-A6)

| Agent | Role | Entry Point | Wrapped Modules |
|-------|------|-------------|-----------------|
| **A1. DataAgent** | 수집 및 정규화 | `src.agents.data_agent` | Collectors (Market, FRED, ECOS, etc.) |
| **A2. SignalAgent** | 이상징후 감지 및 토픽 생성 | `src.agents.signal_agent` | Topic Gate, Engine, Candidate Gate, IssueSignal |
| **A3. NarrativeAgent** | 지능 레이어 및 점수 산출 | `src.agents.narrative_agent` | Narrative Intelligence, Freshness, Scoreboard |
| **A4. DecisionAgent** | 승인 및 최종 의사결정 카드 | `src.agents.decision_agent` | Final Decision Card, Approval Gate, Health Check |
| **A5. VideoAgent** | 영상 후보군 추출 | `src.agents.video_agent` | Video Intelligence Layer |
| **A6. PublishAgent** | SSOT 자산 배포 (최종) | `src.agents.publish_agent` | Asset Publisher (SSOT), Dashboard Gen |

## 2. 주요 변경 사항

### 2.1 엔트리포인트 표준화
- `src/agents/base.py`를 통해 모든 에이전트가 `--date`, `--dry-run`, `--emit-runlog` 공통 인자를 지원합니다.
- `full_pipeline.yml`이 파편화된 스크립트 호출 방식에서 에이전트 기반 순차 호출 방식으로 리팩토링되었습니다.

### 2.2 가드(CI Guards) 및 계약(Contracts)
- **`docs/spec/AGENT_CONTRACTS.md`**: 에이전트 간 입출력 규격을 명문화했습니다.
- **`scripts/verify_agent_contracts.py`**: 에이전트 실행 후 산출물이 계약을 준수하는지 검증합니다.
- **`scripts/verify_no_cross_layer_imports.py`**: UI/Publish 레이어에서 엔진 로직을 직접 참조하거나 점수를 계산하는 등의 계층 위반을 차단합니다.

## 3. 검증 결과 (Verification)

- **로컬 Dry-Run**: 모든 에이전트(A1~A6)의 엔트리포인트 정상 작동 확인 (`--dry-run` 테스트 완료).
- **계층 격리 테스트**: `verify_no_cross_layer_imports.py`를 통해 불필요한 의존성 제거 확인.
- **출력 동일성**: 기존 `today.json`, `manifest.json` 등의 산출물 구조가 유지됨을 확인 (No Behavior Change).

## 4. 향후 운영 가이드
- 에이전트 실행 및 트러블슈팅은 [AGENT_RUNBOOK.md](file:///Users/jihopa/Downloads/HoinInsight_Remote/docs/spec/AGENT_RUNBOOK.md)를 참고하십시오.
- 새로운 데이터 소스 추가 시 `A1. DataAgent`에 등록하고, 새로운 지능 로직 추가 시 `A3. NarrativeAgent`에 등록하는 것을 권장합니다.

---
**Status**: ✅ Phase 21 Completed (Modularization & Contracts)
**Commit**: `[PHASE 21] Agent Modularization EntryPoints + Contracts (No Behavior Change)`
