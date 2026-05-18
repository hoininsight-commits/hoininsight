# Phase 22A: Script Intelligence Layer v1.0

본 문서는 영상 제작 자동화를 위한 **Script Intelligence Layer**의 사양과 인터페이스 정의를 다룹니다.

## 1. 개요 (Purpose)
VideoAgent에 의해 선정된 영상 후보군(Top 1~3)에 대해, 즉시 스크립트 제작이 가능한 수준의 텍스트 패키지를 생성합니다. 이를 통해 엔진의 분석 결과를 최종 미디어 포맷으로 전환하는 병목을 제거합니다.

## 2. 입출력 정의 (I/O)

### 입력 (Inputs)
- `data_outputs/ops/video_candidate_pool.json`: VideoAgent가 선정한 후보 리스트.
- `data/ops/narrative_intelligence_v2.json`: 상세 서술 및 스코어 근거.
- `data/decision/YYYY/MM/DD/final_decision_card.json`: 최종 결정 및 인과 관계 정보.

### 출력 (Outputs)
- `data_outputs/ops/video_script_pack.json`: UI 렌더링용 구조화 데이터.
- `data_outputs/ops/video_script_pack.md`: 사람이 즉시 읽고 녹음할 수 있는 마크다운 형식.

## 3. 데이터 계약 (Contracts)

### video_script_pack.json Schema
```json
{
  "generated_at": "ISO8601",
  "date_kst": "YYYY-MM-DD",
  "candidates": [
    {
      "dataset_id": "string",
      "title": "string",
      "script": {
        "hook": "string",
        "one_min_summary_3lines": ["string", "string", "string"],
        "causal_chain": {
          "cause": "string",
          "structural_shift": "string",
          "market_consequence": "string"
        },
        "evidence_bullets": ["string"],
        "mentionables": [{"ticker": "string", "reason": "string", "risk": "string"}],
        "closing": "string"
      }
    }
  ]
}
```

## 4. 파이프라인 흐름
1. **VideoAgent (A5)**: 후보군 선정 후 `video_script_intelligence_layer.py` 실행.
2. **Script Intelligence Layer**: 산출물 정합성 확인 후 텍스트 생성.
3. **PublishAgent (A6)**: 생성된 `video_script_pack.json` 및 `.md`를 `docs/data/ops/`로 벌크 복사.

## 5. UI/CI 검증 정책
- **Menu**: 메인 UI 내 `#video` 앵커를 통한 단일 진입.
- **Guard**: `verify_remote_pages_contract.py`에서 원격 엔드포인트의 스크립트 필드 존재 여부(hook, causal_chain 등)를 체크.
- **SSOT**: 퍼블리셔(`A6`)는 변형 없이 복사만 수행함을 보장.
