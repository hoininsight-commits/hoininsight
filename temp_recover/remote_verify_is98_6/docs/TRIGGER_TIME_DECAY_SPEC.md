# TRIGGER TIME DECAY SPECIFICATION (IS-33)

## 1. 개요 (Overview)
트리거의 권위와 신선도는 시간이 경과함에 따라 감쇄합니다. 본 엔진은 트리거가 발생한 시점부터 현재까지의 시간을 계산하여 신뢰도(Confidence)를 조절하고, 그에 따른 상태 전이를 관리합니다.

## 2. 신뢰도 감쇄 모델 (Decay Model)

### 기본 설정
- **Initial Confidence**: 100% (기본값)
- **Max Lifetime**: 48시간 (기본값, 트리거 유형에 따라 조절 가능)
- **Decay Curve**: 선형(Linear) 감쇄

### 계산식
`Current Confidence = Initial Confidence * (1 - (Elapsed Hours / Max Lifetime))`

## 3. 상태 전이 규칙 (State Transition Rules)

신뢰도 점수에 따라 트리거의 상태(State)를 결정하며, 하위 상태로의 전이는 불가역적입니다.

| 신뢰도 점수 | 한국어 상태명 (Label) | 설명 |
| :--- | :--- | :--- |
| 70점 이상 | **활성 (ACTIVE)** | 신호가 강력하며 즉시 분석 및 발화 가능 |
| 40점 ~ 69점 | **보류 (HOLD)** | 신호가 약화됨. 추가 증거가 없는 한 발화 유예 |
| 40점 미만 | **침묵 (SILENT)** | 신호 소멸. 대시보드에서 숨기거나 아카이브 처리 |

## 4. 재활성화 조건 (Re-arm Condition)

새로운 **독립적 하드 에비던스(Independent Hard Evidence)**가 확보될 경우에만 신뢰도를 부분적으로 복원할 수 있습니다.

- **복원 공식**: `Current Confidence = min(100, Current Confidence + 30)`
- **제한**: 단순 뉴스(MAJOR_MEDIA)나 재인용 보도는 재활성화에 사용할 수 없음. 공식 문서(OFFICIAL/REGULATORY) 및 공시(FILING)만 인정됨.

## 5. 한국어 로컬라이제이션 (Korean Localization)

대시보드 노출 시 모든 용어는 한국어로 표시됩니다.

- `ACTIVE` -> **활성**
- `HOLD` -> **보류**
- `SILENT` -> **침묵**
- `Time Since Trigger` -> **트리거 발생 후 경과 시간**
- `Remaining Confidence` -> **잔여 신뢰도**
