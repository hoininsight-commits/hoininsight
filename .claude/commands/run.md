# /run — HOIN 파이프라인 실행

프로젝트 루트: `/Users/jihopa/.gemini/antigravity/scratch/HoinInsight`

## 전체 실행 (AGENT-01 ~ AGENT-06)
```bash
cd /Users/jihopa/.gemini/antigravity/scratch/HoinInsight
python -m src.pipeline
```

## 에이전트 개별 실행
```bash
python -m src.agents.collector    # AGENT-01: 시장 데이터
python -m src.agents.learner      # AGENT-02: 유튜브 자막
python -m src.agents.detector     # AGENT-03: 신호 감지
python -m src.agents.analyst      # AGENT-04: 레벨2 분석 (Gemini 필요)
python -m src.agents.writer       # AGENT-05: 스크립트 생성 (Gemini 필요)
python -m src.agents.publisher    # AGENT-06: 대시보드 업데이트
```

## 실행 전 체크
1. `.env` 파일에 필요한 API 키 확인
2. 프로젝트 루트에서 실행 (cwd 중요)
3. AGENT-04, 05 실행 시 GEMINI_API_KEY 필수

## 결과 확인
```bash
cat dashboard/today_brief.txt
```
