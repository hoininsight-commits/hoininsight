# HOIN Operator UI

## 🎯 목적
HOIN Engine의 매일 결정 산출물(JSON)을 시각화하여 콘텐츠 운영자가 오늘 제작할 내용을 3분 안에 파악하고 결정할 수 있도록 돕는 도구입니다.

## 🧭 주요 섹션 안내
1. **오늘의 콘텐츠 상태**: READY(즉시 제작), HYPOTHESIS(가설 기반 추적), HOLD(데이터 대기) 상태를 확인합니다.
2. **오늘의 핵심 이슈**: 오늘 가장 주목해야 할 시장의 변곡점과 '왜 지금인가(Why Now)'를 요약합니다.
3. **말하기 가이드**: 상태에 따른 운영자의 톤앤매너 가이드를 제공합니다. (예: "가능성 프레임으로 말하세요")
4. **로직 체인**: 왜 이 이슈가 선정되었는지에 대한 3단 논리(원인→구조→결과)를 보여줍니다.
5. **종목 및 콘텐츠 팩**: 언급해야 할 종목 리스트와 롱폼/숏폼 제작 정보를 제공합니다.

## 📱 사용 방법
- 별도의 설치나 설정 없이 `index.html`을 브라우저(PC/Mobile)로 열면 됩니다.
- 위에서 아래로 스크롤하며 오늘 할 일과 주의사항을 체크하세요.

## 🧱 기술 사양 (Deterministic UI)
- **Data Source**: `data/decision/*.json`
- **Logic**: Vanilla JS (Render.js) - No LLM, No Backend.
- **Responsive**: PC (Multi-column) / Mobile (Single-column).
