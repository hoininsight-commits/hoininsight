# Decision Card Audit
**생성 시각**: 2026-02-23 12:28:02

**요약**: Complete 0개 / Incomplete 22개 / 전체 22개

## TOP3 Incomplete 원인

1. **status=CANDIDATE (editorial schema)**: 21/22건
   - editorial_selection_*.json 의 모든 pick 이 status=CANDIDATE → 아직 승인 전
   - 승인(status=APPROVED)된 신호가 없는 게 근본 원인

2. **data_incomplete 필드 자체가 없음**: 22/22건
   - 모든 파일에 `data_incomplete` 필드가 없음
   - UI 어댑터가 absence를 truthy로 판단하지 않도록 방어 필요

3. **speakability/status가 OK가 아님**: 22/22건
   - EDITORIAL_CANDIDATE, CANDIDATE, HOLD 상태가 incomplete로 분류됨

## 결론

**Complete 0개는 현재 데이터 기준 정상 상태**이다.
- editorial_selection 전체가 CANDIDATE (미승인)
- today.json도 EDITORIAL_CANDIDATE (permission_granted=False)
- APPROVED/PUBLISHED 신호가 존재하지 않음

## 카드별 상세

| file | schema | date | title | speakability | intensity | why_now_type | ui_class |
|------|--------|------|-------|-------------|-----------|-------------|----------|
| today.json | decision_card |  | 미 국채 10년물 4.24 (➖ +0.33%) | EDITORIAL_CANDIDATE | 0 | DATA | incomplete |
| editorial_selection_2026-02-23.json | editorial | 2026-02-23 | 예정된 'FOMC 의사록 공개'와 구조적 이슈의 충돌  | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-22.json | editorial | 2026-02-22 | 예정된 'FOMC 의사록 공개'와 구조적 이슈의 충돌  | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-21.json | editorial | 2026-02-21 | 예정된 'FOMC 의사록 공개'와 구조적 이슈의 충돌  | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-20.json | editorial | 2026-02-20 | 예정된 'FOMC 의사록 공개'와 구조적 이슈의 충돌  | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-19.json | editorial | 2026-02-19 | 예정된 'FOMC 의사록 공개'와 구조적 이슈의 충돌  | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-18.json | editorial | 2026-02-18 | 예정된 'FOMC 의사록 공개'와 구조적 이슈의 충돌  | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-17.json | editorial | 2026-02-17 | 예정된 'FOMC 의사록 공개'와 구조적 이슈의 충돌  | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-16.json | editorial | 2026-02-16 | 예정된 'FOMC 의사록 공개'와 구조적 이슈의 충돌  | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-15.json | editorial | 2026-02-15 | 예정된 'FOMC 의사록 공개'와 구조적 이슈의 충돌  | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-14.json | editorial | 2026-02-14 | 예정된 'FOMC 의사록 공개'와 구조적 이슈의 충돌  | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-13.json | editorial | 2026-02-13 | 예정된 'FOMC 의사록 공개'와 구조적 이슈의 충돌  | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-12.json | editorial | 2026-02-12 | 예정된 'FOMC 의사록 공개'와 구조적 이슈의 충돌  | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-11.json | editorial | 2026-02-11 | 예정된 'FOMC 의사록 공개'와 구조적 이슈의 충돌  | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-10.json | editorial | 2026-02-10 | 예정된 'FOMC 의사록 공개'와 구조적 이슈의 충돌  | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-09.json | editorial | 2026-02-09 | [D-0] NVIDIA (NVDA) 실적 발표 사전 점 | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-08.json | editorial | 2026-02-08 | [D-1] NVIDIA (NVDA) 실적 발표 사전 점 | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-06.json | editorial | 2026-02-06 | [D-3] NVIDIA (NVDA) 실적 발표 사전 점 | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-05.json | editorial | 2026-02-05 | [D-5] NVIDIA (NVDA) 실적 발표 사전 점 | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-04.json | editorial | 2026-02-04 | [D-6] NVIDIA (NVDA) 실적 발표 사전 점 | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-03.json | editorial | 2026-02-03 | [D-6] NVIDIA (NVDA) 실적 발표 사전 점 | HOLD | 100 | PREVIEW | incomplete |
| editorial_selection_2026-02-02.json | editorial | 2026-02-02 | [D-7] NVIDIA (NVDA) 실적 발표 사전 점 | HOLD | 100 | PREVIEW | incomplete |
