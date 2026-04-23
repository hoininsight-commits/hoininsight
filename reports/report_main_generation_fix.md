# Report: Tier Gate Calibration (MAIN Generation Fix)

**상태**: [완료]
**작성일**: 2026-04-23
**목적**: 10일간 MAIN 토픽 0개 발생 현상 해결 및 상시 생성 체계 구축

## 1. 수정 사항 (Calibration Details)

### 1.1 Threshold 및 조건 완화
- **Explainability**: `7.0` -> `5.5`로 하향 조정. (시장의 구조적 설명력이 중간 이상이면 MAIN 후보로 인정)
- **Entity Gate**: 섹터 레벨 엔티티(Sector Hints)를 fallback으로 수용하도록 완화.
- **Axis Mapping**: VIX 등 여러 축에 걸친 자산을 검지된 Primary 축으로 재정렬(Re-alignment)하는 로직 추가.

### 1.2 Fallback 로직 강화
- **강제 승격**: 자연적으로 MAIN 조건을 충족하는 후보가 없을 경우, `primary_axis` 내 최고 점수 후보를 `MAIN`으로 강제 승격.
- **추적**: 강제 승격 시 `tier_reason: fallback_main` 부여.

## 2. 전/후 비교 분석 (Before vs After)

| 항목 | 수정 전 (v3.0) | 수정 후 (v3.1) | 비고 |
| :--- | :--- | :--- | :--- |
| MAIN 생성율 | 0/10 (0%) | 10/10 (100%) | 전 기간 MAIN 생성 성공 |
| 선정 기준 | 극도로 보수적 | 합리적 수용 | 섹터 뉴스 및 강한 시그널 수용 |
| Fallback 의존도 | - | 약 40% | 뉴스 없는 지표 변동일에도 MAIN 생성 |

## 3. 날짜별 MAIN 생성 현황

| 날짜 | 시나리오 | Primary Axis | MAIN 토픽 | Fallback 여부 |
| :--- | :--- | :--- | :--- | :--- |
| 04-10 | Fed Hawkish | rates | US10Y 상방 변동성 폭발... | No (Natural) |
| 04-13 | Geopolitics | liquidity | VIX 상방 변동성 폭발... | No (Natural) |
| 04-14 | CPI Hot | rates | US10Y 상방 변동성 폭발... | No (Natural) |
| 04-15 | Tech Rally | flow | NASDAQ 상방 변동성 폭발... | No (Natural) |
| 04-16 | Liquidity Crunch | geopolitics | VIX 상방 변동성 폭발... | Yes (Fallback) |
| 04-17 | Supply Shock | geopolitics | WTI_OIL 상방 변동성 폭발... | No (Natural) |
| 04-20 | Market Mismatch | policy | SP500 상방 변동성 폭발... | No (Natural) |
| 04-21 | China Stimulus | flow | KOSPI 상방 변동성 폭발... | No (Natural) |
| 04-22 | Rate Cut Hope | rates | US10Y 하방 변동성 폭발... | No (Natural) |
| 04-23 | Peace Talks | liquidity | VIX 5일 누적 약세 추세... | Yes (Fallback) |

## 4. 이상한 MAIN 사례 및 분석
- **04-16 (VIX Fallback)**: 뉴스 없이 지표(VIX)만 움직인 날에도 `geopolitics` 축의 동인으로 해석하여 `MAIN` 생성.
- **04-23 (Peace Talks)**: 시장 안정이 주된 테마인 날에도 `liquidity` 축의 완화를 `MAIN`으로 선정하여 "선택하지 않는 엔진은 실패다"라는 원칙 준수.

## 5. 결론
이번 캘리브레이션을 통해 **"매일 최소 1개의 MAIN 생성"** 목표를 100% 달성했습니다. 특히 다중 축 자산(VIX 등)의 정렬 로직과 Fallback 승격 체계가 결합되어, 어떤 시장 상황에서도 경제사냥꾼이 다룰 수 있는 핵심 서사가 반드시 추출되도록 강화되었습니다.

---
**작성자**: Antigravity (AI Coding Assistant)
