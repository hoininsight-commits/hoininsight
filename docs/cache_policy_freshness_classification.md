# Classification: Data Freshness Sensitivity — HOIN Insight (#080-TASK-2)

This document classifies all HOIN Insight data sources based on their sensitivity to time and their direct impact on the "WHY NOW" narrative trigger.

## 🟢 A. 저빈도 구조 데이터 (LOW SENSITIVITY)

| 데이터 소스 | 분류 이유 | WHY NOW 영향 | 캐시 적절성 평가 |
| :--- | :--- | :--- | :--- |
| **FRED / ECOS Macro** | 월간/분기별로 발표되며, 값이 하루 중 변하지 않음. | 장기 구조적 배경(Structural Frame) 제공. | **적절**. 하루 1회 수집으로도 충분함. |
| **Consensus (Economic Calendar)** | 향후 이벤트 일정은 고정적임. | "오늘 예정된 이벤트" 필터링에 사용. | **적절**. 하루 시작 시 수집되면 하루 종일 유효. |

## 🟡 B. 중간 민감도 데이터 (MID SENSITIVITY)

| 데이터 소스 | 분류 이유 | WHY NOW 영향 | 캐시 적절성 평가 |
| :--- | :--- | :--- | :--- |
| **Market Index (KOSPI, SPX)** | 장중 지속적으로 변하나, '오늘의 주제'를 바꿀 정도의 추세는 수 시간 단위로 형성됨. | 시장의 심리적 지지선 붕괴 여부 판단. | **보통**. 장마감 후 1회 수집은 위험함(장중 변화 대응 불가). |
| **DART 공시** | 수시로 올라오지만, 대형 호재/악재는 하루 중 특정 시점에 집중됨. | 특정 기업/섹터의 진입 병목(Bottleneck) 해소 감지. | **부족**. 하루 1회 수집 시 오후에 터진 핵심 공시를 놓침. |
| **COT / Flow Data** | 일간/주간 단위의 자금 흐름을 보여줌. | 스마트 머니의 포지션 변화(Smart Money Track) 감지. | **적절**. 데이터 자체가 일간/주간 단위로 생성됨. |

## 🔴 C. 고민감도 데이터 (HIGH SENSITIVITY)

| 데이터 소스 | 분류 이유 | WHY NOW 영향 | 캐시 적절성 평가 |
| :--- | :--- | :--- | :--- |
| **RSS 뉴스/헤드라인** | 매 분마다 새로운 이벤트가 발생하며, "지금 이 순간"의 트리거가 됨. | **핵심 WHY NOW**. 뉴스Mismatch나 돌발 악재 탐지의 근거. | **심각한 부족**. 24시간 캐시는 실시간 뉴스 분석을 불가능하게 만듦. |
| **Fear & Greed Index** | 시장의 극단적 공포/탐욕은 뉴스 하나에 수십 포인트가 출렁임. | 시장의 감정 극단(Extreme Sentiment) 포착. | **부족**. 캐시가 없더라도 수집 빈도가 낮으면 변동을 놓칠 수 있음. |
| **VIX / Market Volatility** | 시장의 '발작'을 가장 먼저 보여주는 데이터. | 리스크 엔진(Risk Engine)의 작동 트리거. | **부족**. 장중 발작 발생 시 24시간 전 캐시 데이터는 무의미함. |

## 🎯 "WHY NOW" 관점 요약

HOIN Insight의 엔진은 **"과거의 지표(A) 위에 현재의 흐름(B)을 얹고, 찰나의 뉴스(C)로 방점을 찍는"** 구조입니다. 
따라서 **C(고민감도) 항목**에 대해 A와 동일한 '당일 파일 존재 시 스킵' 정책을 적용하는 것은 엔진의 눈을 가리는 것과 같습니다.
