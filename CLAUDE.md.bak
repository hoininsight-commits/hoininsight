# HOIN Insight v3.0 — Claude Code 작업 지침서

## 프로젝트 정체성
HOIN Insight는 경제사냥꾼 유튜브 채널 스타일의 경제 콘텐츠를
자동 생성하는 AI 파이프라인이다.
매일 시장 데이터를 수집해서 레벨2 신호를 포착하고
스크립트 초안을 생성해서 선장(운영자)에게 브리핑한다.

## 절대 규칙
- 모든 커뮤니케이션은 한국어
- 코드 변수명/함수명/파일명은 영어 허용
- data/ 폴더 내 기존 데이터 삭제 금지
- archive/ 폴더 내용 삭제 금지
- secrets는 환경변수로만 관리 (코드 하드코딩 금지)

## 프로젝트 구조

```
HoinInsight/
├── src/
│   ├── agents/          ← 6개 에이전트 (핵심)
│   │   ├── collector.py   AGENT-01: 시장 데이터 수집
│   │   ├── learner.py     AGENT-02: 경사 유튜브 자막 수집
│   │   ├── detector.py    AGENT-03: 신호 감지 + 토픽 선정
│   │   ├── analyst.py     AGENT-04: Claude API 레벨2 분석
│   │   ├── writer.py      AGENT-05: 스크립트 생성
│   │   └── publisher.py   AGENT-06: 대시보드 업데이트
│   ├── core/
│   │   ├── sector_map.py  종목-섹터 매핑 (절대 삭제 금지)
│   │   ├── claude_client.py Claude API 래퍼
│   │   └── filters.py     7개 신호 감지 필터
│   └── pipeline.py        전체 파이프라인 오케스트레이터
├── data/
│   ├── raw/YYYYMMDD/      수집된 원시 데이터
│   ├── signals/YYYYMMDD/  감지된 신호
│   ├── analysis/YYYYMMDD/ 분석 결과
│   ├── scripts/YYYYMMDD/  생성된 스크립트
│   ├── learning/          경사 유튜브 학습 데이터
│   └── history/           전체 이력
├── tests/
│   ├── fixtures/          테스트용 가짜 데이터
│   ├── harness.py         전체 파이프라인 테스트
│   ├── test_collector.py  AGENT-01 검증
│   ├── test_detector.py   AGENT-03 검증
│   └── test_analyst.py    AGENT-04 검증
├── dashboard/             GitHub Pages 웹 대시보드
└── archive/               기존 코드 보관 (삭제 금지)
```

## 7개 신호 감지 필터

AGENT-03이 사용하는 토픽 선정 기준이다.

- 필터1: 역사적 임계값 돌파 (N년 만, 역대 최대)
- 필터2: 역설적 현상 감지 (상식과 반대되는 시장 반응)
- 필터3: 가격 미반영 격차 (수혜 구조는 같은데 가격이 다름)
- 필터4: 시의성 (지금 당장, 내일부터)
- 필터5: A→B 연결고리 (전혀 다른 영역으로 파급)
- 필터6: 권위자 행동 변화 (버핏, 이재용 등의 번복/새 행동)
- 필터7: 시장 공포 무관 섹터 (하락장에서도 실적 나오는 곳)

신호 강도 기준:
- 6.0 미만 → 탈락
- 6.0~7.9 → 쇼츠
- 8.0 이상 → 롱폼

## JSON 스키마 (절대 변경 금지)

### today_signal.json 필수 필드
date, topic, strength, content_type, filters_hit,
level2_chain, is_republish, urgency

### today_analysis.json 필수 필드
date, topic, three_lens_analysis(money_flow/structural_change/policy_direction),
level2_chain, historical_reference, risk_factors, check_points

### today_stocks.json 필수 필드
date, topic_signal, stocks(ticker/name/sector/impact/reason)

### content_log.json 필수 필드
contents 배열: id, date, type, title, signal_strength,
is_republish, status

## 검증 명령

```bash
# 전체 테스트 실행
python -m pytest tests/ -v

# 하네스 단독 실행 (가짜 데이터로 파이프라인 전체 테스트)
python tests/harness.py

# 에이전트 개별 실행
python -m src.agents.collector
python -m src.agents.detector
python -m src.agents.analyst
```

## 수정 시 규칙

에이전트 파일 수정 후 반드시:
1. 해당 에이전트 단독 실행 테스트
2. python -m pytest tests/ -v 실행
3. 모두 통과하면 git commit

JSON 스키마 변경 시:
1. tests/fixtures/ 업데이트
2. tests/test_*.py 업데이트
3. dashboard/index.html 바인딩 확인

## 환경변수

ANTHROPIC_API_KEY: Claude API 호출 (AGENT-04, AGENT-05)
ECOS_API_KEY: 한국은행 데이터 (AGENT-01)
FRED_API_KEY: 미 연준 데이터 (AGENT-01)

## GitHub

레포: https://github.com/hoininsight-commits/HoinInsight
브랜치: main
커밋 메시지: 한국어로 작성
