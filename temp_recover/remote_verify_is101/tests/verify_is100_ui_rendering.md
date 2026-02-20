# IS-100-UI Rendering Verification Guide

## 🧪 검증 환경
- 브라우저: Chrome / Safari (Mobile)
- 데이터 상태: `data/decision/` 내의 실제 산출물 기반

## ✅ 검증 체크리스트

### 1. 데이터 인입 및 렌더링 (PC View)
- [ ] 오늘 날짜가 정확히 표시되는가?
- [ ] 상태 뱃지색상(READY-초록, HOLD-빨강, HYPOTHESIS-보라)이 데이터와 일치하는가?
- [ ] 핵심 이슈의 HOOK 문구가 `narrative_skeleton.json`과 일치하는가?
- [ ] 가설 모드일 경우 '가설 비약' 전용 가이드가 출력되는가?

### 2. 반응형 레이아웃 (Mobile View)
- [ ] 가로 너비 375px 이하에서 모든 카드가 단일 컬럼으로 쌓이는가?
- [ ] 텍스트 크기가 모바일 가독성에 적합하게 조정되는가?
- [ ] 종목 카드와 콘텐츠 팩 리스트가 누락 없이 표시되는가?

### 3. 무상태성 및 결정론 검증
- [ ] JSON 파일이 없을 때 적절한 에러/대기 문구가 나오는가?
- [ ] LLM 호출 없이 정적 매핑으로만 정보가 구성되는가?

## 📊 검증 결과 기록
- **Local Verification**: PASS (Browser subagent check)
- **Remote Verification**: [PENDING]
