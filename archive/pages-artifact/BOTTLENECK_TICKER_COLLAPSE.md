# BOTTLENECK_TICKER_COLLAPSE (IS-13)

## 1. 목적 (Purpose)
하나의 IssueSignal 트리거로부터 자본이 이동할 수밖에 없는 "필연적인 대안"을 찾아 1~3개의 Ticker로 압축한다. 이는 단순한 종목 추천이 아니라, 구조적으로 자본이 갇히게 되는(Trapped) 지점을 파악하는 과정이다.

## 2. Collapse 로직 (Logic Flow)
트리거로부터 최종 종목까지의 단계를 논리적으로 좁혀나간다.

1.  **Trigger Match**: 확인된 트리거(READY 상태)가 어떤 실질적 지출(Forced Spend)을 유발하는지 매핑.
2.  **Spend → Bottleneck**: 해당 지출이 반드시 통과해야 하는 병목 지점(기술적, 물리적, 정책적 해치) 식별.
3.  **Bottleneck → Real Tickers**: 병목 현상의 수익을 독점하거나 가장 큰 점유율을 가진 실제 기업으로 압축.

## 3. 강력한 제규 (Hard Rules)
- **수량 제한**: 최종 결과는 반드시 **1~3개**여야 한다.
    - 3개 초과 시: 분석의 해상도가 낮다고 판단하여 **REJECT**.
    - 0개 또는 식별 불가 시: **REJECT**.
- **확정성**: "잠재적 수혜주", "미래의 리더", "만약 ~한다면"과 같은 가설이나 형용사를 배제하고 현재의 구조적 소유권을 기준으로 한다.

## 4. 입출력 (I/O)
- **Input**:
    - `READY` 상태의 트리거 데이터.
    - HoinEngine의 구조적 증거 데이터 (Read-only).
- **Output**:
    - `COLLAPSED_TICKERS`: 1~3개의 확정된 Ticker 리스트 및 각 Ticker의 구조적 역할 설명.
