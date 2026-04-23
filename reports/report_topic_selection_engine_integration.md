# 완료 보고서: 토픽 셀렉션 엔진(Topic Selection Engine) 통합

## 1. 개요
**TOPIC SELECTION ENGINE**이 시스템 문서와 엔진 로직에 공식적으로 통합되었습니다. 이번 작업을 통해 시스템은 단순한 "뉴스 나열" 엔진에서 벗어나, 시장 설명력(Explainability)과 구조적 임팩트를 우선시하는 "서사 선택(Narrative Selection)" 엔진으로 전환되었습니다.

## 2. 문서 작업 결과
- **대상 파일**: [docs/HANDOFF_FINAL.md](file:///Users/taehunlim/dev/HoinInsight/docs/HANDOFF_FINAL.md)
- **수정 사항**:
  - `# 10.3`과 `# 11` 섹션 사이에 `TOPIC SELECTION ENGINE` 블록을 삽입했습니다.
  - 6단계 선택 순서(축 생성 -> 매핑 -> Why Now 필터 -> 설명력 평가 -> 중복 제거 -> 티어 분류)를 정의했습니다.
  - 엄격한 선택 규칙과 "경제사냥꾼(Market Hunter)" 철학을 명시했습니다.
- **참고**: 기존 `TASK #102` 섹션은 문서 맨 마지막에 그대로 유지하여 구현 맥락을 보존했습니다.

## 3. 코드 구현 내용
- **LLM 평가기(Evaluator)**: [src/topic_engine/llm_evaluator.py](file:///Users/taehunlim/dev/HoinInsight/src/topic_engine/llm_evaluator.py)
  - AI 프롬프트를 업데이트하여 `structure_axis`, `why_now_gate`, `explainability_score`, `selection_reason`을 명시적으로 출력하도록 수정했습니다.
  - "경제사냥꾼" 에디터 페르소나 지침을 추가했습니다.
- **토픽 랭커(Ranker)**: [src/topic_engine/topic_ranker.py](file:///Users/taehunlim/dev/HoinInsight/src/topic_engine/topic_ranker.py)
  - **티어링 로직**: `MAIN/TIER_1`, `SECONDARY/TIER_2`, `EARLY/TIER_3` 분류 체계를 구현했습니다.
  - **중복 방지 가드**: 동일한 `structure_axis` 내에서 가장 점수가 높은 후보만 상위 티어로 올라갈 수 있도록 로직을 추가했습니다.
  - **MAIN 선정 엄격 가드**:
    - `why_now_gate`를 반드시 통과해야 함.
    - `explainability_score`가 7.0 이상이어야 함.
    - `entity`가 구체적이어야 함 (`["Market"]`과 같은 일반 명칭 차단).
    - 관련 시장 데이터(`core_facts`)가 반드시 존재해야 함.
  - **ADD-ONLY 원칙**: 기존 점수 체계를 유지하면서 LLM의 정성적 평가 필드를 추가 매핑했습니다.

## 4. 검증 결과
### A. 단위 테스트
- 검증 스크립트 작성: `scratch/verify_selection_engine.py`
- **테스트 케이스 1**: `why_now_gate`를 통과하고 설명력이 높은 후보만 `MAIN`이 되는지 확인.
- **테스트 케이스 2**: 동일 축 내 중복 제거 로직(최상위 1개만 선정) 확인.
- **테스트 케이스 3**: 일반적인 `["Market"]` 엔티티를 가진 토픽이 `MAIN`에서 제외되는지 확인.
- **결과**: `PASS` (모든 테스트 통과)

### B. 샘플 출력 데이터 구조
최종 `topic_selection.json`은 이제 다음 필드를 포함합니다:
```json
{
  "MAIN": {
    "candidate_id": "...",
    "tier": "MAIN/TIER_1",
    "structure_axis": "geopolitics",
    "why_now_gate": {
      "passed": true,
      "recent_change": true,
      ...
    },
    "explainability_score": 9.0,
    "selection_reason": "왜 이 토픽이 선정되었는지..."
  },
  ...
}
```

## 5. TASK #102와의 연결성
이번 작업은 다음을 통해 **TASK #102**를 직접적으로 뒷받침합니다:
1. 구체적인 `entity` 탐지 강제 (MAIN 선정 필수 조건).
2. `market_data` 매핑 강제 (MAIN 선정 필수 조건).
3. 단순 점수제에서 "시장 설명력" 중심의 최종 판단 체계로 전환.

## 6. 완료 조건 체크리스트
- [x] 인수인계 문서 업데이트 (지정된 위치에 삽입)
- [x] TASK #102 섹션 보존
- [x] structure_axis 구현 및 반영
- [x] why_now_gate 로직 반영
- [x] explainability/selection_reason 필드 반영
- [x] 점수만으로 MAIN이 되지 않도록 가드 추가
- [x] 샘플 검증 로그 확인 완료

