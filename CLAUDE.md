# HOIN Insight v3.0

경제사냥꾼 유튜브 채널 AI 파이프라인. 매일 시장 데이터 수집 → 레벨2 신호 감지 → 스크립트 초안 → 운영자 브리핑.

## 절대 규칙
- 모든 커뮤니케이션: **한국어**
- 코드 변수명/함수명/파일명: 영어 허용
- `data/`, `archive/` 폴더 내 기존 파일 **삭제 금지**
- secrets: 환경변수로만 관리 (코드 하드코딩 금지)
- 에이전트 수정 후: 단독 실행 → pytest → git commit

## 에이전트 구조
```
AGENT-01 collector.py   시장 데이터 수집 (yfinance, ECOS, FRED)
AGENT-02 learner.py     경사 유튜브 자막 수집
AGENT-03 detector.py    신호 감지 + 토픽 선정 (7개 필터)
AGENT-04 analyst.py     레벨2 인과관계 분석 (Gemini API)
AGENT-05 writer.py      스크립트 생성 (Gemini API)
AGENT-06 publisher.py   대시보드 업데이트
```

## 신호 강도 기준
- 6.0 미만 → 탈락  |  6.0~7.9 → 쇼츠  |  8.0 이상 → 롱폼

## 7개 필터 (AGENT-03)
필터1 역사적임계값, 필터2 역설적현상, 필터3 가격미반영격차,
필터4 시의성, 필터5 A→B연결고리, 필터6 권위자행동변화, 필터7 시장공포무관섹터

## 환경변수
```
GEMINI_API_KEY    AGENT-04, AGENT-05
ECOS_API_KEY      한국은행 (AGENT-01)
FRED_API_KEY      미 연준 (AGENT-01)
```

## 실행 명령
```bash
python -m src.agents.collector   # AGENT-01
python -m src.agents.detector    # AGENT-03
python -m src.agents.analyst     # AGENT-04
python -m pytest tests/ -v       # 전체 테스트
python tests/harness.py          # 파이프라인 하네스
```

## GitHub
레포: https://github.com/hoininsight-commits/HoinInsight  |  브랜치: main  |  커밋: 한국어
Pages: main → /docs 폴더 서빙

## 상세 컨텍스트
→ WORKING-CONTEXT.md 참조
