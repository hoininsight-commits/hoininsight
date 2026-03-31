# PHASE 23: Structural Regime Layer v1.0

## 1. 개요 (Overview)
Phase 23은 시장의 구조적 상태(Regime)를 정의하여 운영자 및 후속 레이어에 환경 정보를 제공하는 레이어입니다. 엔진의 점수 체계와 독립적으로 작동하며, 거세 지표의 조합을 통해 시장의 기조를 확정합니다.

## 2. 설계 원칙 (Design Principles)
- **No-Behavior-Change**: 엔진 로직, 가중치, 점수에 개입하지 않는 순수 "상태 정의" 레이어입니다.
- **Rule-Based Partitioning**: 확률 모델 대신 명확한 임계값과 지표 조합(Rule-based)을 사용합니다.
- **SSOT**: `regime_state.json`을 통해 전체 시스템에 일관된 상태 정보를 전파합니다.

## 3. 데이터 흐름 (Data Flow)
1. **Macro Data Collection**: Fed Funds, M2, Yield Curve, VIX 등 수집.
2. **Structural Regime Layer**: 지표 조합 기반 상태 판정 (`regime_state.json`).
3. **Publisher (SSOT)**: 자산을 `docs/data/ops/`로 배포.
4. **Dashboard UI**: 최상단에 Regime 배지 및 요약 정보를 렌더링.

## 4. 판정 로직 (Logic)
- **Liquidity**: Fed Funds 수준을 기준으로 `TIGHTENING` / `EASING` 판정.
- **Policy**: 정책 금리 임계값(3.5%)에 따른 `RESTRICTIVE` / `ACCOMMODATIVE` 판정.
- **Risk**: VIX 지수(22/15)를 기준으로 `RISK_OFF` / `RISK_ON` 판정.
- **Yield Curve**: 10Y-2Y 스프레드에 따른 `INVERTED` / `NORMAL` 판정.

## 5. 데이터 스펙 (Data Spec)
### regime_state.json
```json
{
  "generated_at": "ISO8601_TIMESTAMP",
  "date_kst": "YYYY-MM-DD",
  "regime": {
    "liquidity_state": "string",
    "policy_state": "string",
    "risk_state": "string",
    "inflation_trend": "string",
    "yield_curve_state": "string"
  },
  "evidence": [
    {
      "indicator": "string",
      "observation": "string",
      "direction": "string"
    }
  ],
  "regime_summary": {
    "one_liner": "string",
    "structural_bias": "string",
    "risk_note": "string"
  }
}
```

## 6. 검증 항목 (Verification)
- `docs/data/ops/regime_state.json` 존재 및 파싱 확인.
- 필수 상태 필드(liquidity, policy, risk) 값 존재 확인.
- UI 대시보드 상단 배지 노출 정상 확인.
