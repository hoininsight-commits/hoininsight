# HANDOFF — HOIN Insight 현재 상태
최종 업데이트: 2026-04-20

## 현재 버전
v1.0 (2026-04-19 확정)

## 완료된 것
- 대시보드 v2.0 (앰버 터미널 테마, 아카이브 그리드, 스크립트 팝업)
- DETECTOR JSON 파싱 안정화 (extract_json + response_mime_type)
- FACT_CHECKER 수치 오탐 제거 (기간 표현 숫자 스킵)
- publisher.py signal_log 기반 아카이브 복원 (25개 토픽)
- 파이프라인 논리 버그 수정 (start_from 조건문)
- artifact 폴백 강화 (gh api 기반 최신 Run 자동 탐색)
- 프로젝트 지식 관리 구조 구축 (#069)

## 알려진 이슈
- PutCallCollector 403 (API 접근 제한, null 처리 중)
- 과거 아카이브 카드 토픽 품질 낮음 (signal_log 레거시 데이터)
  → 파이프라인 고도화되면 자연스럽게 개선 예정

## 다음 우선순위
1. 스크립트 품질 개선
   - DETECTOR Step 4 COT 표현 명확화
   - "오늘 이것 하나만 기억해" 조건 단일화 (현재 2개 → 1개)
2. Phase 2 준비
   - 유튜브 수집 에이전트 (경제사냥꾼 자막)
   - 코인 수집기 (CoinGecko)

## 에이전트 현재 상태
| 에이전트 | 상태 | 비고 |
|---------|------|------|
| COLLECTOR 7/7 | ✅ | PutCallCollector 403 알려진 이슈 |
| DETECTOR | ✅ | JSON 파싱 안정화 |
| ANALYST | ✅ | |
| WRITER | ✅ | |
| FACT_CHECKER | ✅ | 오탐 제거 완료 |
| PUBLISHER | ✅ | 아카이브 누적 + agent_status 수정 |

## 파이프라인 실행 규칙
- 전체: workflow_dispatch → start_from: collect
- write부터: workflow_dispatch → start_from: write
- publish만: workflow_dispatch → start_from: publish
- push 트리거 = publish만 단독 실행 (검증 불가)
