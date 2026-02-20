# IS-41: Audience Question Anticipation & Control Engine

## 1. Overview
IssueSignal must control the post-signal conversation to maintain authority. This engine predicts possible audience questions and defines strictly controlled responses or silences.

## 2. Core Logic

### 2.1 Anticipation Engine
- **Input**: Signal Object (Trigger, Urgency, Format, Audience).
- **Output**: 3-5 predicted questions in natural Korean tone.
- **Rules**:
  - Based on trigger type (e.g., Earnings -> "Price impact?", Fed -> "Next date?").
  - Based on urgency (High -> "Is it too late?", Low -> "Why now?").

### 2.2 Classification & Response Strategy

| Classification | Meaning | Rule | Response Style |
| :--- | :--- | :--- | :--- |
| **즉답 (ANSWER_NOW)** | Immediate Answer | Non-disclosure safe, timing clarity | Decisive, short Korean sentence |
| **보고 보류 (HOLD)** | Wait and see | Emotional/panic questions | Controlled deferral (e.g. 데이터 확인 후 답한다) |
| **침묵 (SILENT)** | Silence | Ticker reveals, conclusions | Internal reason only, no audience view |
| **브릿지 (DEFER)** | Next Signal Link | Structural expansion | Teaser-style bridge sentence |

## 3. Voice & Language Constraint (IS-39)
- All responses must be **Declarative**.
- **No questions** in the response.
- **Authority**: Use "한다", "결정됐다", "이유는 없다".
- **Localization**: Korean only.

## 4. Dashboard Integration
- New panel: **🗣️ 예상 질문 & 대응 전략**
- Visible fields: Question, Classification (KR), Response.
- Operator fields: Reason (Internal).
