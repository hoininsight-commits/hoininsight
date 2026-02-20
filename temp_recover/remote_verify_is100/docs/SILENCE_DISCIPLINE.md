# SILENCE_DISCIPLINE (IS-16)

## 1. 목적 (Purpose)
IssueSignal은 하루에 최대 3회까지만 발언(Decision Card 생성)할 수 있다. 이는 정보의 희소성(Scarcity)을 유지하고, 편집자적 권위(Editorial Authority)를 확보하며, 인간 사용자의 신뢰를 높이기 위함이다.

## 2. 규율 및 규칙 (Rules)
- **일일 최대 출력**: 하루 최대 3개의 결정 카드(Decision Card)만 허용한다.
- **순위 산정 (Ranking)**: `READY` 상태인 모든 트리거를 다음의 정성적 지표로 평가하여 상위 3개만 선별한다.
    - **자본 결속력 (Capital Force)**: 자본 이동의 규모와 강제성.
    - **시간적 압박 (Time Pressure)**: 즉각적인 대응 필요성.
    - **불가역성 (Irreversibility)**: 사건의 되돌릴 수 없는 성격.
- **침묵의 처리 (Silent Drop)**: 상위 3개에 들지 못한 트리거는 즉시 폐기하며, 로그나 별도의 리스트를 남기지 않는다 (Silence is a feature).

## 3. 강력한 제약 (Hard Constraints)
- **예외 없음**: 어떤 사유로도 일일 3개를 초과할 수 없다.
- **장려상 금지**: "오늘의 주요 뉴스"와 같은 요약 리스트나 언급되지 못한 이슈에 대한 힌트를 제공하지 않는다.

## 4. 구현 로직
`SilenceLayer` 모듈은 내부적으로 당일 생성된 카드의 개수를 추적하고, 트리거 후보군이 발생할 때마다 랭킹을 재산정하여 최종 배포 여부를 결정한다.
