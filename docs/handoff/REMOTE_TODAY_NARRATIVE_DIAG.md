# Remote Today.json Narrative Diagnosis

## 1. Remote `today.json` Fetch Results
We successfully fetched and verified `today.json` from the remote GitHub Pages URL:
`https://hoininsight-commits.github.io/hoininsight/data/decision/today.json`

The payload contains 5 `top_topics`. For all 5 topics, the `narrative_score` is populated but strictly identical:

| Topic | `narrative_score` |
|-------|-------------------|
| `[Monetary Tightening] 미국 소비자물가(CPI) 충격...` | **14.0** |
| `[Monetary Tightening] 미국 개인소비지출(PCE) 물가 이상...` | **14.0** |
| `[Monetary Tightening] 기업 자산 매각(Disposal) 급증...` | **14.0** |
| `[Monetary Tightening] 코스피(KOSPI) 지수 충격...` | **14.0** |
| `[Monetary Tightening] crypto_btc_usd_spot_coingecko L2 Signal...` | **14.0** |

## 2. Root Cause Analysis
We verified the internal calculation within the Engine (`src/ops/narrative_intelligence_layer.py`). The score `14.0` is **NOT** a hardcoded generic fallback or a GUI overlay. It is a genuine output of the Narrative Layer's strict calculation formula:

```python
        intensity = float(card.get("intensity", 50))
        # ...
        actor_weight_score = actor_tier_score * 100.0  # 0 for macros
        base_weighted_sum = (
            0.28 * intensity +       # 0.28 * 50 = 14.0
            0.22 * actor_weight_score +
            0.18 * flow_score +
            0.17 * policy_score +
            0.15 * persistence_score
        )
```

**Why it yields exactly 14.0:**
Because the 5 new Macro Anomalies bridge directly from Engine 1 (`topic_candidates`), they are passing into `issuesignal_today.json` without an explicit `intensity` (0-100) field or `actor` fields.
When `intensity` is `None` or missing, the line `float(card.get("intensity", 50))` applies the default fallback `50`. And since the other qualitative scores (policy/flow/actor) evaluate to `0`, the math strictly executes as `0.28 * 50 = 14.0`.

## 3. Final Conclusion
**CASE T2**: `intensity` fallback 주입에 의한 계산 상수값 (분산 없음).
계산 함수 자체는 통과하지만, Macro topic 객체들이 `intensity` 필드를 누락한 채로 Narrative Layer로 진입하여 디폴트 `50`이 적용되고, 그 결과 수학적으로 일목요연하게 `14.0`만 산출되는 현상입니다. 점수 공식을 수정할 필요 없이, 시더(Seeder)나 이슈시그널 생성 단계에서 원래 Macro가 가졌던 anomaly level/score를 `intensity` 필드에 정상적으로 맵핑해주면 분산이 발생합니다.
