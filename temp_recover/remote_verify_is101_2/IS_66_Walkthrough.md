# IS-66 Editorial Mode Implementation (운영자 편집 모드)

## 1. 개요
본 작업(IS-66)은 IssueSignal 시스템이 엔진의 판단을 더 직관적으로 운영자에게 전달하고, `TRUST_LOCKED` 수준에 도달하지 않은 후보군(Editorial Candidates)도 콘텐츠화할 수 있도록 지원하는 "운영자 편집 모드" 구현입니다.

## 2. 주요 변경 사항

### [IssueSignal] Engine Logic Check
- **다중 후보 선정:** 기존 단일 후보(`selected_candidate`) 선정 방식에서 상위 3개 후보(`top_candidates`)를 선정하는 방식으로 변경되었습니다.
- **Editorial Candidate 상태 추가:**
  - 조건: `HARD_FACT` 존재 + `WHY_NOW` 논리 생성 가능 + (Bottleneck 주인공 또는 기업행동/자본이동 관련).
  - 의미: 엔진이 100% 확신하지 않더라도(Non-LOCKED), 운영자가 판단하여 콘텐츠화할 수 있는 충분한 정보가 갖춰진 상태.
- **스크립트 생성 강제:** `EDITORIAL_CANDIDATE` 상태인 경우 `TRUST_LOCKED`가 아니더라도 반드시 5단계 스크립트를 생성하여 제공합니다.

### [Script Engine] 5-Step Structure
- **스크립트 구조 변경:**
  1. **정의 (Signal):** 이상 신호 포착 선언.
  2. **표면 해석 (Surface):** 시장의 일반적 해석.
  3. **시장의 오해 (Misread):** 반박 및 본질 제시.
  4. **구조적 강제 (Structural Force):** 근본 원인 및 Why Now.
  5. **결론 (Conclusion):** 필연적 흐름 및 행동 촉구.
- **어조:** 한국어 평서문, 단호한 어조 사용 ("~입니다", "필연입니다").

### [Dashboard] Editorial View
- **상단 섹션 개편:** "📌 오늘의 확정 토픽" 단일 뷰에서 "📌 오늘의 콘텐츠 후보 (EDITORIAL VIEW)" 리스트 뷰로 변경되었습니다.
- **기능:**
  - 최대 3개의 후보 카드가 노출됩니다.
  - 각 카드는 [스크립트 보기 & 복사] 버튼을 제공합니다.
  - 버튼 클릭 시 5단계 스크립트 전문이 펼쳐지며, 원클릭 복사가 가능합니다.
- **UI 용어 한국어화:**
  - `TRUST_LOCKED` -> 🔒 발행 확정 (LOCKED)
  - `EDITORIAL_CANDIDATE` -> 📝 편집 후보 (EDITORIAL)
  - `HOLD` -> ⚠️ 편집 검토 (HOLD)

## 3. 검증 결과
- **테스트:** `tests/verify_is66_editorial_logic.py` 통과 (5단계 구조 확인).
- **데이터:** `data/dashboard/today.json` 확인 결과, `editorial_candidates` 리스트가 정상적으로 생성되고 각 후보별 `generated_script`가 포함되어 있음.
- **대시보드:** HTML 생성 로직에 `editorial_candidates` 이터레이션 구조 적용 확인.

## 4. 결론
이제 운영자는 대시보드 접속 즉시 오늘 활용 가능한 토픽 후보군을 확인하고, 스크립트를 바로 복사하여 영상 제작에 착수할 수 있습니다.
