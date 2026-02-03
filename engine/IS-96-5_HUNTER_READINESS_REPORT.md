# IS-96-5: HUNTER READINESS DIAGNOSIS REPORT

## 1. 개요
현재 HOIN Engine의 "경제사냥꾼(Economic Hunter)" 스타일 콘텐츠 생성 능력을 진단한 결과, 핵심 로직은 구현되었으나 **데이터 인입 및 레이어 간 연동 누락**으로 인해 실제 산출물이 생성되지 않고 있음을 확인했습니다.

## 2. 데이터 진단 결과

### 2-1. Hypothesis Jump 항목 수: 0건
- `data/decision/interpretation_units.json` 내 `mode == "HYPOTHESIS_JUMP"` 항목이 존재하지 않습니다.
- 현재 모든 산출물은 기존의 `STRUCTURAL` 모드(정량적 이상징후 기반)로만 생성되고 있습니다.

### 2-2. READY / HOLD / DROP 분포
- **HYPOTHESIS_JUMP**: 해당 없음 (데이터 생성 실패)
- **STRUCTURAL**: READY (1건), HOLD (1건)

### 2-3. 대표 케이스 분석: SpaceX–xAI (TSLA/COHR/RDW)
- **진단**: **가설 점프 입력 자체가 없었음 (A. 데이터 부재)**
- **상세 원인**:
    1. `src/ops/run_content_pack_pipeline.py` 실행 시 `CatalystEventCollector`가 호출되지 않아 `data/ops/catalyst_events.json`이 생성되지 않았습니다.
    2. `src/decision/run_is96_4.py` (Decision Layer Entry)가 모킹된 일반 유닛만 사용하고 있으며, 촉매제 이벤트를 로드하여 `DecisionAssembler`에 전달하는 로직이 빠져 있습니다.

## 3. Narrative Skeleton 및 Tone 진단
- `narrative_skeleton.json` 확인 결과, 가설 전용 훅("지금은 확정이 아니라 가능성이다")이 사용된 사례가 없습니다.
- Speakability Gate에서 가설 로직이 작동할 기회 자체가 없었습니다.

## 4. 최종 결론

> **ENGINE REQUIRES ADDITIONAL CATALYST INPUT**

현재 엔진은 "경제사냥꾼" 콘텐츠를 만들 수 있는 **지능(Logic)은 있으나, 감각(Sensing)과 행동(Integration)이 연결되지 않은 상태**입니다.

## 5. 차기 조치 권고 (Next Actions)
1. **Sensing 연결**: `run_content_pack_pipeline.py`의 첫 단계로 `CatalystEventCollector`를 추가하여 실제 시장의 촉매제 데이터를 확보해야 합니다.
2. **Decision 연동**: `src/decision/run_is96_4.py`를 수정하여 `data/ops/catalyst_events.json`이 존재할 경우 이를 로드하고 `assembler.assemble(units, catalyst_events)`와 같이 전달하도록 보강이 필요합니다.
3. **Threshold 조정**: 가설 기반 콘텐츠의 경우, 일반 구조적 콘텐츠보다 Speakability 문턱값을 낮게 설정하거나 별도의 `Hunter Mode` 플래그를 도입할 것을 권장합니다.

---
**STATUS: ENGINE REQUIRES ADDITIONAL CATALYST INPUT**
**COMMIT_HASH: 3cf7ed40f951e44a4bd177ae84bd2865768e718b (Baseline)**
