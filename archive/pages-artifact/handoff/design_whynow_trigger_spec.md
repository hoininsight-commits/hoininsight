[WHY_NOW_TRIGGER_LAYER_SPEC]

Trigger_1:
- Name: Scheduled Catalyst Arrival
- Structural Definition: A deterministic calendar event with a fixed timestamp that forces market participants to re-evaluate asset pricing before the event occurs.
- Observable Signals:
  * Earnings Release Date (D-Day)
  * Official Product Launch Schedule
  * Conference/Expo Keynote Time
  * Option/Futures Expiry Date
- Narrative Binding Point: Action

Trigger_2:
- Name: Mechanism Activation
- Structural Definition: A regulatory, legal, or infrastructural change in the market operating environment that becomes effective or enforceable at a specific moment.
- Observable Signals:
  * Policy Enforcement Effective Date
  * Court Ruling/Verdict Date
  * Index Rebalancing Implementation Date
  * Tariff/Tax Application Start Date
- Narrative Binding Point: Tension

Trigger_3:
- Name: Smart Money Divergence
- Structural Definition: A statistically significant anomaly where informed capital flow diverges from price action at a specific timestamp, indicating a structural accumulation or distribution.
- Observable Signals:
  * Net Buying Volume > Threshold (vs Price Drop)
  * Insider Trading Filing Date
  * Block Deal Execution Time
  * Basis Divergence Peak
- Narrative Binding Point: Hunt

[REJECTION_RULE]
A topic must be rejected if it relies solely on continuous variable states (e.g., "undervalued", "high growth", "good technology") without a discrete temporal anchor (Timestamp, Effective Date, or Anomaly Instance). If the "Why Now" argument can effectively be used unchanged in 30 days, the topic is structurally invalid and must be discarded.
