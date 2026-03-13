# PRE_TRIGGER_PROMOTION_ENGINE (IS-22)

## 1. 목적 (Purpose)
`PRE_TRIGGER`(선제적 경보) 상태가 언제 침묵을 깨고 `TRIGGER`(활성 트리거)로 승격되어야 하는지를 결정한다. 이는 "더 이상 예고가 아니라, 지금 말하지 않으면 늦는 사건"으로 변하는 변곡점을 포착하기 위함이다.

## 2. 승격 판정 조건 (Promotion Conditions)
다음 4가지 조건 중 **최소 2개 이상**이 충족될 경우 `PRE_TRIGGER`는 `TRIGGER`로 자동 승격된다.

1.  **OFFICIAL ACTION (공식적 행동)**
    - 법안 발의/서명, 정책 시행 공표.
    - 공식 공시, SEC Filing, 정부 공식 발표.
2.  **CAPITAL COMMITMENT POINT (자본 결속 점)**
    - 실질적인 Capex 집행 시작.
    - 공급 계약 체결 공시.
    - 주문 재개 또는 취소의 최종 확정.
3.  **TIME COLLAPSE (시간적 압착)**
    - 일정이 명확히 고정되어 변경 불가능함.
    - 유예(Grace period)나 지연 옵션이 완전히 소멸된 상태.
4.  **MARKET ACKNOWLEDGMENT (시장 인지)**
    - 해당 이슈로 인한 가격 급변동.
    - 수급 불균형(Aggressive bid/ask) 포착.
    - 단일 방향으로의 거래량 집중.

## 3. 승격 거절 (Forbidden Promotion)
단순히 다음의 정보만으로는 승격될 수 없다.
- 기사 한 줄 (익명 보도 등).
- 공식 확인되지 않은 시장 소문.
- 펀더멘털과 무관한 단기적 가격 등락.

## 4. 문장 전환 규칙 (Headline Transition)
승격 시 헤드라인은 반드시 다음 규칙에 따라 변환되어야 한다.

- **PRE_TRIGGER**: "아직 **[사건]**은 터지지 않았지만, **[주체]**는 이미 **[행동]**을 해야 하는 상태다."
- **TRIGGER**: "오늘 **[사건]**이 발생했고, **[주체]**는 더 이상 선택 없이 **[행동]**을 해야 한다."

## 5. 승격 시 액션 (Execution on Promotion)
1.  **State Change**: `state`를 `TRIGGER`로 변경.
2.  **Content Refresh**:
    - PRE_TRIGGER용 8블록 구조에서 TRIGGER용 7블록 구조로 전환.
    - 사건 발생 사실을 반영한 실시간 데이터(IS-19) 주입.
3.  **Quota Consumption**: 승격된 TRIGGER는 당일 발화 제한(3개) 카운트에 포함된다.
4.  **Revalidation**: 종목 압축(Ticker Collapse) 및 무효화 조건(Kill-switch)을 사후 데이터 기준으로 재산정한다.
