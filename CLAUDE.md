# HOIN Insight v3.0 — Claude Code 지침

## 프로젝트
경제사냥꾼 스타일 경제 콘텐츠 자동 생성 AI 파이프라인.
매일 시장 데이터 수집 → 신호 감지 → 스크립트 생성 → 선장 승인.

## 절대 규칙
- 한국어로만 커뮤니케이션
- data/ 폴더 기존 데이터 삭제 금지
- archive/ 폴더 삭제 금지
- .env 파일 git 커밋 금지
- secrets 환경변수로만 관리

## 구조
src/agents/   collector·learner·detector·analyst·writer·publisher
src/core/     filters·gemini_client·config
data/         raw·signals·analysis·scripts·learning·history
tests/        harness·fixtures·test_*.py

## 에이전트 실행 순서
01→02→03→04→05→06 순차 실행
04,05: GEMINI_API_KEY 활성화 완료

## 검증
python -m pytest tests/ -v

## 현황
WORKING-CONTEXT.md 참조

## 출력 규칙 (반드시 준수)
- 작업 완료 후 채팅 출력 금지
- 결과는 파일로만 저장
- 완료 보고는 "✅ 완료" 한 줄만
- 지시서에 명시된 파일만 읽을 것
- 코드 전체를 채팅에 출력하지 말 것

## 출력 규칙 (반드시 준수)
- 완료 보고는 ✅ 완료 한 줄만
- 지시서에 명시된 파일만 읽을 것
- 결과는 파일로만 저장, 채팅 출력 금지
