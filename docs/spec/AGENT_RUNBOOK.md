# Agent Runbook (Phase 21)

본 문서는 HOIN Insight 프로젝트의 각 에이전트를 개별적으로 또는 전체적으로 실행하는 표준 지침을 제공합니다.

## 1. Local Execution (Agent By Agent)

모든 에이전트는 `python -m src.agents.AGENT_NAME` 형식을 통해 개별 실행이 가능합니다.

- **DataAgent (A1)**: `python3 -m src.agents.data_agent`
- **SignalAgent (A2)**: `python3 -m src.agents.signal_agent`
- **NarrativeAgent (A3)**: `python3 -m src.agents.narrative_agent`
- **DecisionAgent (A4)**: `python3 -m src.agents.decision_agent`
- **VideoAgent (A5)**: `python3 -m src.agents.video_agent`
- **PublishAgent (A6)**: `python3 -m src.agents.publish_agent`

### 1.1 Common Parameters
- `--date YYYY-MM-DD`: 특정 날짜를 기준으로 실행하고자 할 때 사용합니다.
- `--dry-run`: 실제 산출물 저장 없이 실행 흐름을 확인하고자 할 때 사용합니다.
- `--emit-runlog`: 실행 정보를 `data_outputs/ops/runlogs/`에 기록합니다.

## 2. Integrated Pipeline (full_pipeline)

`full_pipeline.yml`은 위의 에이전트들을 순차적으로 실행하여 배포 과정을 완료합니다.
**실행 순서**: A1 -> A2 -> A3 -> A4 -> A5 -> A6

## 3. Monitoring & Troubleshooting

실행 중 오류가 발생할 경우 아래 순서로 확인합니다.

1. **Runlogs**: `data_outputs/ops/runlogs/` 하위의 최신 JSON 파일을 확인합니다.
2. **Contracts**: `docs/spec/AGENT_CONTRACTS.md`의 입출력 규격을 준수하는지 점검합니다.
3. **Github Actions Logs**: 파이프라인의 실패 단계에서 스택 트레이스를 확인합니다.

---
*주의: 원본 엔진 로직은 에이전트 래퍼를 통해 간접 호출되므로, 로직 수정 시에는 각 에이전트가 참조하는 src 하위의 원본 모듈을 수정해야 합니다.*
