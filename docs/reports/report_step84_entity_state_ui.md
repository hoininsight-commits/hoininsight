# [Step 84] ENTITY → ACTION INTERPRETATION UI (Decision Surface) 완료 보고서

## 1. 개요
본 단계에서는 Step 83에서 도출된 엔티티들을 단순 나열하는 것을 넘어, **"지금 어떤 상태(State)로 인식해야 하는가?"**를 시각화하는 **Decision Surface(의사결정 표면)**를 구현했습니다. 이는 Economic Hunter가 "뭘 사야 하는가?"가 아닌 "지금 판이 어느 국면인가?"를 직관적으로 파악하도록 돕는 인지 보조 장치입니다.

## 2. 변경 내역

### [NEW] `src/ops/entity_state_classifier.py`
- **역할**: Entity Context를 분석하여 4가지 Action State로 분류.
- **State Logic**:
    - **OBSERVE (Gray)**: 초기 노출 단계. 아직 임계치 미만.
    - **TRACK (Blue)**: 확정된 일정/정책(Locked)이 존재하거나 관심도가 증가하는 단계.
    - **PRESSURE (Orange)**: 구조적 병목(Bottleneck)이 작동하거나 높은 강도(Intensity)의 압박이 진행 중인 단계.
    - **RESOLUTION (Purple)**: 이벤트가 정점에 도달하여 해소 국면에 진입한 단계 (Deep Hunt + High Escalation).
- **Justification**: "왜 이 상태인가?"에 대한 3문장 논리 근거 자동 생성.

### [MODIFY] `src/dashboard/topic_card_renderer.py`
- **역할**: Decision Surface UI 렌더링.
- **UI Design**:
    - **State Badges**: 상태별 컬러 코딩(Gray/Blue/Orange/Purple) 적용.
    - **Justification Panel**: 카드 우측에 판단 근거를 명시하여 블랙박스 의사결정 방지.
    - **Disclaimer**: "행동 지시 아님(Not Advisory)" 문구 강제 삽입.

### [MODIFY] `src/dashboard/dashboard_generator.py`
- **역할**: Classifier 통합.
- **연동**: `EntityMapping` 결과를 `EntityStateClassifier`에 전달하여, 최종적으로 대시보드의 `EntityPool` 하단에 `DecisionSurface` 섹션 추가.

## 3. 검증 결과 (`verify_step84_entity_state_ui.py`)
- **시나리오**: "AI 전력망 붕괴(Deep Hunt)" 위기 상황 시뮬레이션.
- **검증 항목**:
    - **Deep Hunt Logic**: Escalation Count 5 상황에서 `RESOLUTION` 상태로 정확히 전이 확인.
    - **Visuals**: `state-resolution` 클래스 및 Purple 테마 적용 확인.
    - **Safety**: "행동 지시가 아님" 문구 출력 확인.

## 4. 의의
이제 HOIN Insight는 "어떤 종목?"(Step 83)을 넘어 **"어떤 국면?"(Step 84)**까지 제시합니다. 사용자는 이 화면을 통해 **"아직 지켜봐야 할 때(Observe)"**인지, **"이미 결판이 난 때(Resolution)"**인지를 즉각적으로 인지할 수 있게 되었습니다.
