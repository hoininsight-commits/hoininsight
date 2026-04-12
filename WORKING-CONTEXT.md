# HOIN Insight v3.0 — 완전한 프로젝트 컨텍스트
# 새 채팅에서 이 파일 하나만 첨부하면 모든 맥락이 이어진다
# 마지막 업데이트: 2026-04-12

---

## 1. 프로젝트 정체성

**HOIN Insight v3.0** — 경제사냥꾼 유튜브 채널 스타일의 경제 콘텐츠 자동 생성 AI 파이프라인

### 최종 목표
경제 뉴스 1개 입력 → 경제사냥꾼 스타일 완성 스크립트 즉시 출력
매일 KST 06:00 GitHub Actions가 자동 실행 → 선장이 아침에 대시보드 확인 → 승인 → 발행

### GitHub
- 레포: https://github.com/hoininsight-commits/hoininsight
- 대시보드: https://hoininsight-commits.github.io/hoininsight/
- 로컬 경로 (회사 맥북): /Users/jihopa/.gemini/antigravity/scratch/HoinInsight
- 로컬 경로 (집 맥북): ~/dev/HoinInsight

---

## 2. 작업 방식 룰 (반드시 준수)

### 선장-안티 협업 방식
```
선장(웹 Claude): 설계·판단·지시서 작성
안티(Claude Code): 실행·구현·테스트
```

### 지시서 룰
- 모든 작업은 지시서로만 진행 (선장이 직접 작업하는 것 없음)
- 지시서에 코드 전체를 넣지 않음 (토큰 낭비)
  → 코드는 별도 파일로 만들어서 레포에 올리고 지시서는 "실행해라"만
- 완료 보고서 저장 위치: ~/Downloads/HOIN_REPORTS/날짜_작업명/
- 완료 보고서는 반드시 ~/Downloads/에 저장 (레포에 올리지 않음)

### 토큰 절약 룰
- settings.json: model: claude-sonnet-4-6 (회사+집 맥북 모두 적용)
- 지시서는 짧게 — 확인/실행만, 코드 포함 금지
- 새 채팅 시작 시 이 파일(WORKING-CONTEXT.md) 하나만 첨부
- /clear: 완전히 다른 작업 전환 시
- 안티가 코드를 직접 작성할 때만 긴 작업 허용

### 절대 규칙
- 한국어로만 커뮤니케이션
- data/ 폴더 기존 데이터 삭제 금지
- archive/ 폴더 삭제 금지
- .env 파일 git 커밋 금지
- API 키를 채팅창에 붙여넣지 않음

---

## 3. 시스템 아키텍처

### 6개 에이전트 파이프라인
```
AGENT-01 COLLECTOR  → data/raw/YYYYMMDD/ (market/macro/sentiment.json)
AGENT-02 LEARNER    → data/learning/scripts/ (경사 자막 수집)
AGENT-03 DETECTOR   → data/signals/YYYYMMDD/ (candidates.json, today_signal.json)
AGENT-04 ANALYST    → data/analysis/YYYYMMDD/ ← GEMINI_API_KEY 필요 (2026-04-12 활성화)
AGENT-05 WRITER     → data/scripts/YYYYMMDD/  ← GEMINI_API_KEY 필요 (2026-04-12 활성화)
AGENT-06 PUBLISHER  → dashboard/ 업데이트 + 이력 저장
```

### 7개 토픽 선정 필터 (전부 구현됨)
```
필터1: 역사적 임계값 돌파 (환율>1400, VIX>20)
필터2: 역설적 현상 감지 (전쟁뉴스+급등 등)
필터3: 미반영 격차 (환율→수출주 미반영 등)
필터4: 시의성
필터5: A→B 연결고리 (중동→유가→제조업)
필터6: 권위자 행동 변화
필터7: 공포무관섹터 (하락장 방산/바이오)
강도 기준: 8.0↑=롱폼 / 6.0~7.9=쇼츠 / 미만=탈락
```

### 실제 수집 데이터
```
실제 수집:
  환율(KRW=X), KOSPI(^KS11), VIX(^VIX), WTI(CL=F): yfinance
  Fear&Greed: alternative.me API
  뉴스: 연합뉴스+매일경제 RSS

임시값 (API 미연동):
  한국 기준금리: 2.75 고정 (ECOS API 필요)
  미국 기준금리: 4.25 고정 (FRED API 필요)
```

### 최신 파이프라인 실행 결과 (2026-04-11)
```
환율: 1482.7원 / KOSPI: 5858.87 / VIX: 19.23 / WTI: $96.57
토픽: 환율 1483원 + 유가 $96.6 동시 급등 → 복합 위기 신호
강도: 10.0 / 유형: 롱폼
```

---

## 4. 소스 구조 (3차 정리 완료 — 2026-04-11)

```
HoinInsight/
├── CLAUDE.md               ← Claude Code 지침 (35줄, 슬림)
├── WORKING-CONTEXT.md      ← 이 파일
├── requirements.txt
│
├── src/
│   ├── agents/
│   │   ├── collector.py    AGENT-01 (8K)
│   │   ├── learner.py      AGENT-02 (8K)
│   │   ├── detector.py     AGENT-03 (12K)
│   │   ├── analyst.py      AGENT-04 (8K)
│   │   ├── writer.py       AGENT-05 (8K)
│   │   └── publisher.py    AGENT-06 (12K)
│   ├── core/
│   │   ├── filters.py      7개 필터 엔진
│   │   ├── gemini_client.py
│   │   ├── claude_client.py (어댑터)
│   │   └── config.py
│   └── pipeline.py
│
├── tests/
│   ├── harness.py
│   ├── test_collector.py
│   ├── test_detector.py
│   ├── test_analyst.py
│   ├── test_filters.py
│   └── fixtures/
│   (총 73개 test_*.py — pytest 246/246 통과)
│
├── dashboard/              ← 로컬 대시보드 데이터
├── docs/                   ← GitHub Pages 서빙
├── data/                   ← 수집 데이터 (git 미추적)
├── archive/                ← 구버전 보관
└── .github/workflows/
    └── daily_hoin_engine.yml  ← 매일 KST 06:00 자동 실행
```

---

## 5. 완료된 지시서 이력

| 지시서 | 커밋 | 내용 |
|--------|------|------|
| #001 Phase1 | bb1210708 | 기반구조, AGENT-01, yfinance 실제 수집 |
| #002 Phase2 | 277e22ec6 | AGENT-02,03,04 구현 |
| #002수정 Gemini전환 | abea16c79 | Gemini API 전환 + AGENT-02 단순화 |
| #003 Harness | 8fce64d52 | CLAUDE.md + pytest |
| #004 Writer/Pub | 301429a59 | AGENT-05,06 구현 |
| #005 대시보드/Actions | d2cd4cf62 | 대시보드 + GitHub Actions |
| #006 대시보드v2 | 5c1373e01 | 운영자 대시보드 4구역 |
| 임시 Pages수정 | 1aea60212 | docs/ 배포 경로 수정 |
| 임시 프롬프트뷰어 | 85fcb1155 | Gemini 레벨2 프롬프트 뷰어 추가 |
| 임시 토큰최적화 | — | settings.json sonnet 전환 |
| #007 데이터수집 | a481fac7b | Fear&Greed 실제수집, 뉴스RSS |
| 임시 대시보드경로 | e0e2f1cdf | today_data.json 위치 통일 |
| #008 필터고도화 | 29208d551 | 필터2,3,5,7 실제 구현 pytest 27/27 |
| #009 Actions수정 | d1c397b45 | contents:write 권한 + 에러핸들링 |
| 임시 CLAUDE.md복원 | 5cb32e91e | CLAUDE.md 정상 복원 |
| 임시 Actions수동실행 | e9496295 (bot) | Actions 성공 확인 |
| 임시 소스리팩토링 1차 | ad71023ab | 47개 파일 삭제 |
| 임시 소스리팩토링 2차 | 8882407b8 | 161개 파일 정리 (228MB) |
| 임시 소스리팩토링 3차 | 5666e90fe | pytest 246/246 달성 |
| 임시 GEMINI_API_KEY | — | GitHub Secret 등록 + AGENT-04,05 활성화 |
| 임시 CONTEXT업데이트 | — | WORKING-CONTEXT.md 최종 전면 교체 |

---

## 6. 현재 시스템 상태

### 완료
- [x] AGENT-01~06 구현 완료
- [x] 필터 1~7 모두 구현
- [x] 대시보드 GitHub Pages 배포
- [x] GitHub Actions 매일 KST 06:00 자동 실행
- [x] pytest 246/246 통과 (에러 0, 실패 0)
- [x] 소스 트리 3차 정리 완료 (클린)
- [x] GEMINI_API_KEY GitHub Secret 등록 (2026-04-12)
- [x] AGENT-04, AGENT-05 Actions 주석 해제 (2026-04-12)

### 대기 중 (선장 직접 수행 필요)
- [ ] GitHub Secrets 추가 등록
      → ECOS_API_KEY, FRED_API_KEY
      → github.com/hoininsight-commits/hoininsight/settings/secrets/actions
- [ ] 집 맥북 .env 파일 입력 (회사 맥북에서 키 확인 후)

### 알려진 미완성
- 한국 기준금리/M2: 임시값 (ECOS API 미연동)
- 미국 기준금리: 임시값 (FRED API 미연동)
- KOSPI 0.00% 등락: 장 마감 후 수집 시 발생 (정상)

---

## 7. 다음 작업 우선순위

```
1순위: AGENT-04,05 실제 실행 확인 (내일 KST 06:00 Actions 자동 실행)
       → 오전에 대시보드 확인
       → analysis/scripts 데이터 생성 여부 확인

2순위: ECOS/FRED API 연동
       → 기준금리 실제 수집
       → 임시값 제거

3순위: 로컬 운영자 대시보드 고도화
       → 실시간 파이프라인 실행 버튼
       → 스크립트 미리보기
       → 승인 버튼
```

---

## 8. API 키 현황

```
ECOS_API_KEY:       .env 있음 (회사 맥북) / GitHub Secrets 미등록
FRED_API_KEY:       .env 있음 (회사 맥북) / GitHub Secrets 미등록
GEMINI_API_KEY:     GitHub Secret 등록 완료 (2026-04-12) / .env 미입력
ANTHROPIC_API_KEY:  미설정

집 맥북 .env:       회사 가서 키 확인 후 입력 필요
```

---

## 9. 환경 정보

```
회사 맥북:
  경로: /Users/jihopa/.gemini/antigravity/scratch/HoinInsight
  Claude Code: 정상 설치
  settings.json: model=claude-sonnet-4-6

집 맥북:
  경로: ~/dev/HoinInsight
  Claude Code: 정상 설치
  settings.json: model=claude-sonnet-4-6
  .env: 키 미입력 (회사에서 확인 후 입력 필요)
```

---

## 10. 새 채팅 시작 방법

새 채팅에서 이 파일을 첨부하고 아래 메시지를 보낸다:

```
이 파일은 HOIN Insight v3.0 프로젝트의 전체 컨텍스트입니다.
읽고 나서 현재 상태를 요약해주고 다음 작업을 제안해줘.
```

그러면 새 Claude가 모든 맥락을 파악하고 바로 이어서 작업할 수 있다.

---

## JSON 스키마 (절대 변경 금지)

### today_signal.json
`date, topic, strength, content_type, filters_hit, level2_chain, is_republish, urgency`

### today_analysis.json
`date, topic, three_lens_analysis(money_flow/structural_change/policy_direction), level2_chain, historical_reference, risk_factors, check_points`

### today_stocks.json
`date, topic_signal, stocks(ticker/name/sector/impact/reason)`

### content_log.json
`contents[]`: `id, date, type, title, signal_strength, is_republish, status`

## 데이터 경로 구조
```
data/raw/YYYYMMDD/market.json
data/signals/YYYYMMDD/today_signal.json
data/signals/YYYYMMDD/candidates.json
data/analysis/YYYYMMDD/today_analysis.json
data/analysis/YYYYMMDD/today_stocks.json
data/scripts/YYYYMMDD/longform_script.md
data/history/signal_log.json
data/history/content_log.json
dashboard/today_data.json       ← publisher가 최종 생성
```

## Git 충돌 대응 패턴
원격 자동화 커밋과 충돌 시:
```bash
git stash
git pull --rebase
# 충돌 시: git checkout --ours [file] && git add [file] && git rebase --continue
git push
git stash pop
```
