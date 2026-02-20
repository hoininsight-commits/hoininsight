# TICKER_PATH_EXTRACTOR_SPEC.md

본 문서는 매크로/섹터 주인공(Actor)을 실제 데이터(HARD_FACT) 기반의 구체적인 종목(Ticker)과 연결하는 IS-69 Ticker Path Extractor의 상세 규격을 정의합니다.

## 1. 개요 및 헌법 준수
- **목표**: "주인공(섹터/자본) → 병목(구조) → 종목(티커)"의 논리적 사슬을 실데이터로 완성.
- **데이터 원칙**: SEC 8-K, 공식 RSS, 매크로 지표 등 `HARD_FACT` 기반일 때만 종목을 도출한다.
- **안전 규칙**: 기사(TEXT_HINT) 기반의 티커 도출은 금지하며, 신뢰도 60점 미만은 노출하지 않는다.

## 2. 데이터 스키마 (Ticker Path)

```json
{
  "ticker_results": [
    {
      "ticker": "AAPL",
      "company_name_ko": "애플",
      "event_type": "계약 | 인수 | 투자 | 생산증설 | 파트너십 | 규제",
      "bottleneck_link_ko": "병목 연결 문장 (1문장)",
      "confidence": 85,
      "evidence_url": "8-K 링크",
      "exposure": "공개 | 마스킹 | 숨김"
    }
  ],
  "global_bottleneck_ko": "전체 구조적 병목 설명 (1문장)"
}
```

## 3. 핵심 로직: Ticker Path Extractor

### 3-1. Candidate Pool 수집
- 최근 48시간 내 `corporate_facts` 중 `HARD_FACT` 등급인 항목 추출.
- `event_type` 분류: `계약(Contract)`, `인수(M&A)`, `CAPEX(Investment)`, `증설(Expansion)`, `파트너십(Partnership)`, `규제(Regulation)`.

### 3-2. Actor Alignment (정합성)
주인공(Actor)의 성격과 기업 이벤트의 키워드가 일치하는지 검증합니다.

| Actor Tag | 매칭 키워드 (Event Context) |
| :--- | :--- |
| **수혜** | "Sales", "Contract", "Supply", "Expansion", "Profit" |
| **피해 / 회피** | "Regulation", "Lawsuit", "Loss", "Divestiture" |
| **병목 / 대체** | "Exclusive", "Patent", "Bottleneck", "Unique", "Sole" |

### 3-3. Confidence Scoring
- **기본**: 60점 (HARD_FACT)
- **Actor Tag 일치**: +10점
- **독점/특허 키워드 포함**: +10점
- **최근 24시간 내 발생**: +10점
- **신뢰도 80점 이상**: "공개"
- **60~79점**: "마스킹" (예: A***)
- **60점 미만**: "숨김"

## 4. UI 및 내러티브 가이드 (한글 100%)

- **내러티브**: 스크립트 4단계(구조적 강제)에서 "병목 → 종목"을 "A사는 ~한 독점 계약을 통해 시장의 병목을 해소하고 있습니다."와 같이 평서문으로 삽입.
- **대시보드**: 상단 카드에 `🎯 도출 종목` 섹션과 `🔗 병목 연결` 문장을 배치.
- **라벨링**: ✅증거, 🟡보통, 🔍단서 배지 사용.
