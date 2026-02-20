# IS-43: Post-Emission Outcome & Accuracy Engine

## 1. Overview
IssueSignal authority is built on accountability. This engine tracks the real-world outcome of every signal—published, held, or silenced—to verify accuracy and refine future decisions.

## 2. Tracking Logic

### 2.1 Post-Emission Monitoring
- **Scope**: All signals (Status: READY/HOLD/SILENT).
- **Time Windows**:
  - 즉각적 (24~48시간): 초기 반응 및 변동성 확인.
  - 단기 (1~2주): 내러티브의 현실화 여부 확인.
- **Metrics**: 변동성 변화율, 가격 방향성 부합도, 수급 집중도.

### 2.2 Outcome Classification (Korean)
| Classification | Meaning | Condition |
| :--- | :--- | :--- |
| **정확 (ON-TIME)** | Accurate & timely | Prediction matches reality in 48h |
| **너무 빠름 (EARLY)** | Prediction too early | Narrative valid but market moved later |
| **너무 늦음 (LATE)** | Prediction too late | Market already pivoted before emission |
| **과도함 (OVERSTATED)** | Overstated impact | Narrative valid but volatility was minor |
| **침묵이 옳았음 (SILENCE_CORRECT)** | Correct Silence | Dropped signal indeed failed to emerge |

## 3. Learning Memory
- **Storage**: Outcomes are indexed by Trigger type, Sector, and Class.
- **Usage**: Future calibration. Does not alter history.
- **Output**: Daily accuracy summary statistics.

## 4. Dashboard Integration
- New panel: **📊 발화 결과 & 정확도 (OUTCOME & ACCURACY)**
- Display:
  - Accuracy distribution (N items).
  - Silence accuracy rate.
  - Repeated Early/Late error heatmap by sector/type.

## 5. Localization
- All labels in Korean.
- No visibility of English internal status codes to operator.
