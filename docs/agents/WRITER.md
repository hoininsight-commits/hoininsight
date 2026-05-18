# WRITER 설계 원칙
v1.0 | 2026-04-20

## 역할
분석된 논리 구조를 바탕으로 "경제사냥꾼" 페르소나를 투영한 7단계 빌드업 유튜브 스크립트를 작성한다.

## 입력 / 출력
- **입력**: `today_analysis.json`, `today_stocks.json`, ‘Writer Prompt’
- **출력**: `today_script_long.md`, `today_script_short.md` (유튜브 제목 포함)

## 핵심 로직
1. **Persona Injection**: 단정적 어미, 짧은 문장, 숫자 중심 서사 적용
2. **7-Stage Build-up**: 
   - Hook(모순) → Conflict(충돌) → Mechanism(구조) → Why Now(임계점) → Implication(영향) → Mentionables(종목) → Risk(시나리오)
3. **Constraint Enforcement**: 
   - "역대급", "미친 듯이" 등 금지 표현 필터링
   - 데이터 없는 행위자 추측 금지 (수치 근거 필수)
4. **Scenarios A/B/C**: 현재 상황의 유지, 악화, 반전 시나리오를 각각 정량적 조건과 함께 제시

## 수정 시 주의사항
- `writer_prompt.py`의 금지 목록 업데이트 시 즉각 반영 필요
- 반말(사냥꾼 화법)과 존댓말(표준 리포트) 분리 로직 안정성 유지

## 알려진 이슈
- 가끔 임계점(Why Now) 설명 시 구체적 수치 대신 추상적 묘사를 하는 경향 (프롬프트 강화 중)
