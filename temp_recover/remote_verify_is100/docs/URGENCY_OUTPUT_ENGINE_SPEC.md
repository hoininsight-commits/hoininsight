# URGENCY & OUTPUT ENGINE SPECIFICATION (IS-34)

## 1. 개요 (Overview)
본 엔진은 트리거의 단순 유효성을 넘어, 해당 정보를 "지금 당장" 발화해야 하는지(Urgency)와 어떤 형식(Output Form)이 가장 적합한지를 결정합니다. 이는 IssueSignal이 단순 '진실 탐지기'에서 '편집적 결단 엔진'으로 진화하는 핵심 단계입니다.

## 2. 발화 압력 점수 (Urgency Score)

각 트리거에 대해 0~100점의 점수를 산출합니다.

### 주요 평가 요소 (Factors)
- **시간적 압박 (Time Pressure)**: 의사결정 윈도우 마감 임박 여부. (가중치 40%)
- **자본 투입의 불가역성 (Capital Commitment Irreversibility)**: 한 번 실행되면 되돌리기 힘든 자본 흐름 관련성. (가중치 30%)
- **정책/실행 컷오프 (Policy Cutoff Proximity)**: 법안 시행이나 정책 발표 시점과의 근접성. (가중치 20%)
- **대체 경로 가용성 (Alternative Path Availability)**: 해당 정보 외에 다른 판단 근거가 존재하는지 여부. (가중치 10%)

## 3. 출력 형식 결정 (Output Form Decision)

발화 압력 점수에 따라 최적의 소통 형식을 결정합니다.

| Urgency Score | 출력 형식 (Output Form) | 설명 |
| :--- | :--- | :--- |
| 90점 이상 | **대형 영상 (LONG FORM)** | 경제 헌터 메인 영상 제작 대상 |
| 70점 ~ 89점 | **숏츠 (SHORT FORM)** | 핵심 내용 위주의 짧은 영상 |
| 50점 ~ 69점 | **텍스트 카드 (TEXT ONLY)** | 텍스트 기반 카드 뉴스 또는 알림 |
| 50점 미만 | **침묵 (SILENT)** | 정보를 보유하되 대외 발화하지 않음 |

## 4. '너무 늦음' 오버라이드 (Too-Late Override)

트리거가 '활성' 상태라 하더라도, 다음 조건 중 하나를 만족하면 강제로 **침묵(SILENT)** 처리합니다.

- **이미 선반영됨 (Already Priced-in)**: 시장 가격에 해당 정보가 충분히 반영된 징후 포착.
- **이미 실행됨 (Already Executed)**: 관련 의사결정이나 정책이 이미 실행 완료되어 실익이 없음.
- **높은 시장 인지도 (High Awareness)**: 이미 대다수의 시장 참여자가 인지하고 있어 정보 비대칭성이 사라짐.

이 오버라이드는 새로운 '하드 에비던스'가 등장하지 않는 한 불가역적입니다.

## 5. 한국어 로컬라이제이션 (Korean Localization)

| 용어 | 한국어 레이블 |
| :--- | :--- |
| Urgency Score | **발화 압력 점수** |
| Output Form | **출력 형식** |
| Why Now / Why Silent | **지금 말해야 하는 이유 / 침묵하는 이유** |
| Already Priced-in | **이미 가격에 반영됨** |
| Already Executed | **이미 실행 완료됨** |
| High Awareness | **시장 인지도 높음** |
