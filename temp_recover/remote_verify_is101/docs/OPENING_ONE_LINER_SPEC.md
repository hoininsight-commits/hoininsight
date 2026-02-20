# IS-73 Auto Opening One-Liner Specification

## 1. Objective
Synthesize a single, authoritative Korean sentence ("Opening One-Liner") that explains "Why Now" based on the Decision Tree output. This sentence serves as the top-level explanation for the Operator Decision Mode.

## 2. Hard Constraints
- **Strict Tone Lock**: No speculation words (e.g., "가능성", "전망", "추정", "될 수").
- **100% Korean UI**: No English labels.
- **Production Only**: No mocks, no future dates.
- **Verified Evidence Only**: Use TRUST chain, Quote proof, Hard facts, WHY-NOW.
- **One Sentence**: Short and punchy (recommended 28-45 characters).

## 3. Logic & Templates

### A) Success Case (Topic Selected)
Priority Order:
1.  **Existing WHY-NOW Sentence**: If available, use it directly (it's already validated).
2.  **Derived from Decision Tree**:
    - Template 1: "오늘 [시점 필연성] 때문에 [주체]는 [강제 행동]해야 하고, 자본은 [목적지]로 이동한다."
    - Template 2: "지금 [외부 변수]가 확정됐고, [주체]의 선택지는 닫혔다."
    - Template 3: "오늘의 핵심은 [병목]이며, 이 병목이 자본을 [방향]으로 밀어 넣는다."

### B) Failure Case (No Topic)
Derive from `first_fail_node` in Decision Tree.

| Failed Node | Output Message (One-Liner) |
| :--- | :--- |
| **데이터 수집 (DA)** | "오늘은 수집된 유의미한 데이터 신호가 없어 침묵한다." |
| **팩트 체크 (HF)** | "오늘은 확증 가능한 하드 팩트가 부족하여 발화를 중단한다." |
| **시점 분석 (WN)** | "오늘 반드시 말해야 할 시점(WHY-NOW) 조건이 충족되지 않았다." |
| **주인공 매칭 (AM)** | "이슈를 주도할 명확한 주인공(수혜/피해)이 식별되지 않았다." |
| **품질 하한선 (QF)** | "최종 품질 기준(스크립트 생성 불가 등) 미달로 발화를 보류한다." |
| **(기타/Unknown)** | "오늘은 확정 조건을 넘지 못해 침묵한다." |

## 4. Tone Lock (Banned Words)
The following words/patterns are strictly forbidden in the synthesized sentence:
- `가능` (possibility)
- `전망` (forecast)
- `추정` (estimation)
- `예상` (expectation)
- `보인다` (seems)
- `~일 수` (could be)
- `~할 것` (future tense speculation)

## 5. Input Requirements
- **Top Topic Object**: Must contain `decision_tree_data`, `actor`, `why_now` (optional), `tickers`.
- **Decision Tree**: List of nodes with status `PASS` or `FAIL`.

## 6. Output Implementation
- **Function**: `synthesize_opening_one_liner(top_topic: dict, decision_tree_data: list) -> str`
- **Location**: `src/issuesignal/opening_one_liner.py`
