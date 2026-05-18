# 파이프라인 설계 원칙
v1.0 | 2026-04-19 확정

## 4개 Job 구조
collect → intelligence → write → publish

## 실행 트리거 규칙
| 트리거 | 실행되는 Job |
|--------|------------|
| 매일 06:00 KST (schedule) | 전체 |
| workflow_dispatch: collect | 전체 |
| workflow_dispatch: intelligence | intelligence → write → publish |
| workflow_dispatch: write | write → publish |
| workflow_dispatch: publish | publish만 |
| git push (경로 불일치) | publish만 |

## Artifact 계승 규칙
- collect 스킵 → 직전 raw_data artifact로 intelligence 실행
- intelligence 스킵 → 직전 analysis_data artifact로 write 실행
- write 스킵 → 직전 script_data artifact로 publish 실행
- publish는 항상 실행 (파이프라인 완결 보장)

## 이상징후 탐지 4관점
1. SPEED: Z-score > 2.0 또는 5일 변화율 급변
2. CORRELATION: 원래 같이/반대로 가야 하는 지표가 반대 방향
3. NEWS_MISMATCH: 뉴스 톤과 지표 방향이 반대
4. WHY_NOW: 오늘 처음 나타난 변화

## 토픽 선정 우선순위
1순위: 컨센서스 서프라이즈 (예상치 대비 5% 이상 괴리)
2순위: 지표 간 모순 (CORRELATION 붕괴)
3순위: Z-score 이상 이탈 (SPEED 신호)
Fallback: Z-score 최대값 → None

## 토픽 선정 5기준 (모두 충족)
1. 모순이 있어야 한다
2. WHY NOW가 데이터로 설명 가능
3. 구조적 확장이 가능 (A→B→C→한국 투자자 임팩트)
4. 시청자가 즉시 납득 가능
5. 종목/행동까지 연결 가능

## 스크립트 7단계 구조
1. Hook: 시장의 모순 한 문장
2. Expectation vs Reality: 기대와 현실 충돌
3. Mechanism: 구조적 원인 (금리/유동성/정책)
4. WHY NOW: 왜 하필 지금인가
5. Implication: 포지션별 임팩트 분리
6. Mentionables: 연결 종목/섹터
7. Risk: 시나리오 A/B/C + "오늘 이것 하나만 기억해"

## 절대 금지 토픽 패턴
- "환율 1478원 돌파" → 절대값, 매일 같은 상황
- Z-score나 서프라이즈 수치 없이 뉴스 키워드만 있는 토픽
- "왜 오늘인가"를 데이터로 설명 못하는 토픽

## API 실패 처리
- 수집 실패 시 해당 필드 null 저장 (0.0 가짜 정상값 금지)
- 텔레그램 브리핑 상단에 ⚠️ [수집 경고] 블록 자동 주입
