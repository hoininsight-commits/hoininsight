# PHASE 22B: Structural Stock Linkage Layer v1.0

## 1. 개요 (Overview)
Phase 22B는 VideoAgent가 선별한 토픽과 실제 시장의 업종/종목을 구조적으로 연결하는 레이어입니다. 기존에 스크립트 내부에 하드코딩되어 있던 종목 정보를 독립적인 연계 레이어로 분리하여 SSOT(Single Source of Truth)로 관리합니다.

## 2. 설계 원칙 (Design Principles)
- **No-Behavior-Change**: 엔진의 핵심 점수나 로직에 영향을 주지 않는 단순 매핑 레이어입니다.
- **Deterministic Mapping**: Axis(Policy, Liquidity 등) 정보를 기반으로 사전에 정의된 업종 및 종목을 연결합니다.
- **Zero Leak**: 이 레이어에서 매수/매도 권유나 새로운 투자 점수를 생성하지 않습니다.

## 3. 데이터 흐름 (Data Flow)
1. **Video Intelligence Layer**: 영상 후보군 선정 (`video_candidate_pool.json`).
2. **Structural Stock Linkage Layer**: 후보의 Axis 정보를 기반으로 업종/종목 매핑 (`stock_linkage_pack.json`).
3. **Script Intelligence Layer**: 생성된 Linkage Pack을 참조하여 스크립트 내 Mentionables 구성.
4. **Publisher (SSOT)**: 모든 자산을 `docs/data/ops/`로 배포.

## 4. 데이터 스펙 (Data Spec)
### stock_linkage_pack.json
```json
{
  "generated_at": "ISO8601_TIMESTAMP",
  "date_kst": "YYYY-MM-DD",
  "topics": [
    {
      "dataset_id": "string",
      "axis": ["string"],
      "industry_exposure": [
        {
          "industry": "string",
          "logic": "string"
        }
      ],
      "stocks": [
        {
          "ticker": "string",
          "name": "string",
          "exposure_type": "string",
          "risk_note": "string"
        }
      ]
    }
  ]
}
```

## 5. 검증 항목 (Verification)
### 로컬/CI 무결성
- `docs/data/ops/stock_linkage_pack.json` 존재 여부 및 JSON 파싱.
- 각 토픽에 `dataset_id`, `stocks` 필드 필수 포함.

### 원격 계약 검증
- 엔드포인트 `200 OK` 확인.
- 최소 1개 이상의 유효한 토픽 데이터 존재 여부 확인.
