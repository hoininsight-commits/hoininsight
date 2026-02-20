# [IS-102] SCHEDULE_RISK_CALENDAR 검증 리포트

## 1. 개요
본 리포트는 [IS-102] 스케줄 리스크 캘린더 레이어(Schedule Risk Calendar Layer)의 구현 및 UI 통합 결과를 검증합니다. 이 레이어는 향후 90일/180일간의 확정 및 예상 리스크 일정을 점수화하여 운영자에게 타임라인 형태로 제공합니다.

## 2. 검증 환경 (REMOTE Protocol)
- **Repo**: https://github.com/hoininsight-commits/HoinInsight.git
- **Clone Strategy**: Clean Clone (`remote_verify_is102`)
- **Baseline Commit**: `31de2454e76961f630856037dd7626960ac71195`
- **Current Commit**: `0b0740a510d6da5dc23cd1d68c9db765ef356e65`

## 3. 구현 내용 (Add-Only Integrity)
- [x] **New Registry**: `registry/schedules/schedule_registry_v1.yml` 추가 (KR/US/Global 일정).
- [x] **New Generator**: `src/ui/schedule_risk_calendar.py` 추가.
- [x] **Scoring Logic**: Proximity(근접도), Theme Boost(오늘의 주제 연관성), Market Sensitivity(시장 민감도) 반영.
- [x] **New Assets**: `data/ui/schedule_risk_calendar_{90,180}d.json`, `data/ui/upcoming_risk_topN.json` 생성.
- [x] **UI Enhancement**: `docs/ui/render.js` 수정으로 "Top 7 리스크" 카드 그리드 및 "180일 전체 캘린더" 토글 섹션 추가.
- [x] **Pipeline Integration**: `src/engine/__init__.py` 내에 선택적 레이어로 통합.

## 4. 테스트 결과 (Unit Tests)
`tests/verify_is102_schedule_risk_calendar.py` 실행 결과:

| Test Case | Description | Result |
| :--- | :--- | :--- |
| `test_calendar_generation` | 파일 생성, 정렬 규칙, `ESTIMATE` 캡(0.6) 적용 여부 검증 | ✅ PASS |

## 5. UI 가시성 및 기능 확인
- **Upcoming Risks**: 상단에 배치되어 90일 내 가장 중요한 7개 일정을 한눈에 파악.
- **Collapsible Calendar**: 180일 내의 모든 리스크 일정을 테이블 형태로 상세 조회 가능.
- **Natural Language**: "금리 경로 재평가", "패시브 자금 리밸런싱" 등 쉬운 한국어 설명 제공.

## 6. 최종 판정
✅ **PASS**

본 모듈은 [IS-102] 요구사항을 완벽히 충족하며, 경제사냥꾼 콘텐츠의 "리스크 타임라인"을 엔진 기반으로 자동 생성하는 기반을 마련했습니다.
