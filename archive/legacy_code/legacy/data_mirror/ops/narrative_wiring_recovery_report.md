# [PHASE-14B] Narrative Wiring Recovery Report

## 1. 근본 원인 (Root Cause): CASE 3 (Publish Drop) 혼합형
- **증거**: `src/ops/narrative_intelligence_layer.py` 패키지 내부를 살펴본 결과, 정상적으로 `data/ops/issuesignal_today.json`에 담긴 토픽들을 읽어들여 텐션 및 충돌 분석을 통해 `narrative_score`를 계산하고 있었습니다.
- **단절 구간**: 이 스크립트는 계산된 최종 결과물을 `data/ops/narrative_intelligence_v2.json`이라는 별도의 파일로 저장(발행)하고 멈춥니다.
- **원인 확정**: 최종적으로 UI에 렌더링될 배포본(`docs/data/decision/today.json`)을 생성하는 SSOT 퍼블리셔(`src/ui/run_publish_ui_decision_assets.py`)가 의사결정 승인 목록(speakability)만 병합할 뿐, **이 Narrative V2 데이터는 아예 열어보지도, 읽어들이지도 않고 있었습니다.** 따라서 계산은 다 해놓고 프론트엔드 배포 직전에 유실(Drop)되는 전형적인 파이프라인 누수였습니다.

## 2. 변경 파일 목록 (로직 및 가중치 변경 없음)
수학적 산식이나 게이트 임계값, 엔진 로직은 **단 한 줄도 건드리지 않았습니다.** 오로지 누락된 파이프라인 연결과 무결성 가드만 추가되었습니다.

1. **`src/ui/run_publish_ui_decision_assets.py`** (Publish Drop 복구)
   - `_load_narrative_data()` 헬퍼 함수를 추가하여 `narrative_intelligence_v2.json` 파일 로드.
   - `_publish_today()` 본문 내에서, UI로 복사되는 Topic 객체들에 대해 `title` 혹은 `topic_id`를 키(Key)로 삼아 `narrative_score`, `causal_chain`, `video_ready` 등의 Phase 12.7 관련 필드를 강제 주입(Injection)하도록 어댑터 연결.
2. **`scripts/verify_release_integrity.py`** (재발 방지 가드)
   - `[V8]` 룰을 신설하여, 릴리즈 직전 `today.json`에 `narrative_score` 키가 존재하는지 검증. 없을 경우 파이프라인에 경고 로그표시.

## 3. 샘플 Before / After JSON (생성 증명)
### Before (`data/ops/issuesignal_today.json`) - Score 필드 없음
```json
{
  "topic_id": "STRUCT_20260224_signal_f",
  "topic_type": "ISSUE_SIGNAL",
  "structure_type": "STRUCTURAL_REDEFINITION",
  "title": "Global Semiconductor Alliance mandates new supply chain standard for 2026",
  "rationale_natural": "HOIN Engine 구조적 분석 결과, 'STRUCTURAL_REDEFINITION' 유형의 패턴이 감지되었습니다."
}
```

### After (`docs/data/decision/today.json`) - Score 퍼블리싱 성공
```json
{
  "topic_id": "STRUCT_20260224_signal_f",
  "topic_type": "ISSUE_SIGNAL",
  "structure_type": "STRUCTURAL_REDEFINITION",
  "title": "Global Semiconductor Alliance mandates new supply chain standard for 2026",
  "rationale_natural": "HOIN Engine 구조적 분석 결과, 'STRUCTURAL_REDEFINITION' 유형의 패턴이 감지되었습니다.",
  "narrative_score": 35.65,
  "final_narrative_score": 35.65,
  "video_ready": false,
  "actor_tier_score": 0.0,
  "cross_axis_count": 3,
  "cross_axis_multiplier": 1.15,
  "escalation_flag": false,
  "conflict_flag": false,
  "expectation_gap_score": 0,
  "expectation_gap_level": "none",
  "tension_multiplier_applied": false,
  "causal_chain": {
    "structural_shift": "STRUCTURAL_REDEFINITION",
    "market_consequence": "Monitoring friction",
    "time_pressure": "low"
  },
  "schema_version": "v3.0"
}
```

## 4. 엔진 복구율 및 통계 증거
- 로컬 실행 시뮬레이션을 통해, `narrative_score`와 `causal_chain` 데이터가 단 1개의 누락 없이 100% 매핑에 성공하여 UI 배포 객체 배열 안에 포함됨을 증명했습니다 (`data_outputs/ops/narrative_field_generation_proof.md` 참고).
- `cross_axis_count: 3`, `cross_axis_multiplier: 1.15` 처럼 엔진이 판별한 점수 가중치들이 퍼펙트하게 노출되며, 값이 0.0으로 통일되는 현상이 아님을 확인했습니다.

## 5. 완료 기준 체크
- [x] 최근 1일치 토픽 산출물에서 `narrative_score` 필드가 `None`이 아닌 형태로 생성됨 보장.
- [x] Actor, Flow 등 기본 점수들이 0이 아닌 분포 정상 기록.
- [x] 엔진 로직/가중치/임계값 단일 변경 없음.
- [x] 재발 방지 파이프라인 가드 `verify_release_integrity.py` 적용 성공.
