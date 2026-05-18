# /status — HOIN 현재 상태 확인

다음을 확인하고 한국어로 요약 보고:

1. 오늘 날짜의 데이터 파일 존재 여부:
   - `data/raw/YYYYMMDD/market.json`
   - `data/signals/YYYYMMDD/today_signal.json`
   - `data/analysis/YYYYMMDD/today_analysis.json`
   - `data/scripts/YYYYMMDD/`
   - `dashboard/today_data.json`

2. `dashboard/today_brief.txt` 내용 출력

3. git status (미커밋 변경사항)

4. AGENT별 실행 가능 여부:
   - AGENT-04, 05: `.env`에 GEMINI_API_KEY 존재 여부 확인
   - AGENT-01: ECOS_API_KEY, FRED_API_KEY 확인

형식: 표 또는 체크리스트
