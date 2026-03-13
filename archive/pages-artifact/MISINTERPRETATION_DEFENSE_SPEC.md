# IS-42: Misinterpretation Risk & Defense Engine

## 1. Overview
IssueSignal signals must be protected from misuse or misunderstanding. This engine identifies potential risks of misinterpretation and injects defensive language to ensure authority and clarity.

## 2. Core Logic

### 2.1 Misinterpretation Scenario Engine
- **Input**: Signal Object.
- **Output**: 3-5 predicted scenarios in Korean.
- **Example Scenarios**:
  - 금융적 오해: "지금 당장 풀매수하라는 뜻인가?"
  - 티커 한정 오해: "이 기업 하나에만 올인하면 되는가?"
  - 결과 확정 오해: "무조건 수익이 보장되는 결과인가?"

### 2.2 Risk Level Classification
- **낮음 (LOW)**: 맥락 소실 정도.
- **중간 (MEDIUM)**: 내러티브 왜곡 가능성.
- **높음 (HIGH)**: 직접적인 금전적 피해나 법적 오해 리스크.

### 2.3 Defensive Statement Generation
- **Target**: MEDIUM/HIGH Risk scenarios.
- **Style**: Declarative, authoritative (IS-39 Voice Lock). NO emotional disclaimers.
- **Examples**:
  - "이 신호는 단기 매수 지시가 아니다."
  - "행동의 책임은 자본의 주인에게 있다."
  - "분석은 구조적 변화만을 보고한다."

## 3. Auto-Insertion Rules
- **텍스트 카드**: 하단에 병기.
- **쇼츠 스크립트**: 마지막 문장에 삽입.
- **롱폼 스크립트**: '5. 결론' 직전에 삽입.

## 4. Dashboard Integration
- New panel: **⚠️ 오해 리스크 & 방어 장치 (DEFENSE ENGINE)**
- Fields: Scenario, Risk Level (KR), Defense Applied (Yes/No), Override Status.

## 5. Voice & Language
- Korean only.
- Spoken Korean tone.
- Decisive endings (다, 라).
