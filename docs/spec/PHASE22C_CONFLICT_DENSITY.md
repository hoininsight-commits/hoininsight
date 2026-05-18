# PHASE 22C: Conflict Density Upgrade Layer v1.0

## 1. 개요 (Overview)
Phase 22C는 Conflict/Escalation 탐지율을 높이기 위해 토픽의 서술 밀도를 보강하는 레이어입니다. 점수나 임계값을 수정하지 않고, 입력 내러티브를 축(Axis) 결합 및 구조화된 문장으로 재구성하여 상충 지점을 명확히 드러내는 데 목적이 있습니다.

## 2. 설계 원칙 (Design Principles)
- **No-Behavior-Change**: 엔진의 판단 로직을 건드리지 않고 입력 데이터의 "질"만 높입니다.
- **Explainable Conflict**: 상충 후보(Contradiction Pair)를 명시하여 탐지 결과에 대한 설명가능성을 확보합니다.
- **SSOT Integrity**: 모든 보강 데이터는 `conflict_density_pack.json`을 통해 관리됩니다.

## 3. 데이터 흐름 (Data Flow)
1. **Narrative Intelligence Layer**: 기초 내러티브 생성.
2. **Conflict Density Layer**: Axis 결합 및 상충 후보 도출 (`conflict_density_pack.json`).
3. **Conflict Detection Engine**: 보강된 데이터를 기반으로 최종 Conflict Flag 판단 (Legacy 로직 유지).
4. **Publisher (SSOT)**: 자산을 `docs/data/ops/`로 배포.

## 4. 핵심 로직 (Core Logic)
- **Axis 결합**: 최소 2개 이상의 축(예: Policy + Liquidity)을 결합하여 다각도 분석 텍스트 생성.
- **Contradiction Pair**: `src/ops/conflict_pair_map.py`를 통해 상호 모순되는 시그널 조합(예: Rate Up + Flow In) 탐지 및 텍스트화.

## 5. 데이터 스펙 (Data Spec)
### conflict_density_pack.json
```json
{
  "generated_at": "ISO8601_TIMESTAMP",
  "date_kst": "YYYY-MM-DD",
  "topics": [
    {
      "dataset_id": "string",
      "density_text": {
        "summary": "string",
        "structured_paragraph": ["string"],
        "contradiction_pairs": [
          {
            "pattern": "string",
            "description": "string",
            "lhs_label": "string",
            "rhs_label": "string"
          }
        ]
      }
    }
  ]
}
```

## 6. 검증 항목 (Verification)
### 로컬/CI 무결성
- `docs/data/ops/conflict_density_pack.json` 존재 및 파싱 확인.
- `structured_paragraph`의 길이(3줄 이상) 및 필수 필드 존재 확인.

### 원격 계약 검증
- 엔드포인트 `200 OK` 확인.
- 원격 데이터 파싱 및 고밀도 텍스트 구성 확인.
