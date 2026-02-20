# ACTOR_BRIDGE_SPEC.md

본 문서는 매크로 신호(Macro Signals)를 구체적인 주체(Actor)와 연결하여 발화 가치를 부여하는 IS-68 Actor Bridge Layer의 상세 규격을 정의합니다.

## 1. Actor 정의 및 출력 스키마

주인공(Actor)은 아래 세 가지 유형 중 하나로 정의됩니다.

| 유형 | 설명 | 예시 |
| :--- | :--- | :--- |
| **기업 (Company)** | 구체적인 상장사 또는 법인 | 코닝(GLW), 애플(AAPL) |
| **섹터 (Sector)** | 산업군 또는 테마 | 방산 섹터, 에너지 섹터 |
| **자본주체 (Capital Actor)** | 거시적인 자본 흐름의 주체 | 미국 장기채, 월가 자본 |
| **없음 (None)** | 주체 도출 실패 | - |

### JSON Schema
```json
{
  "actor_type": "기업 | 섹터 | 자본주체 | 없음",
  "actor_name_ko": "한글 표시명",
  "actor_reason_ko": "주체 선정 사유 (2~4문장, 근거 등급 포함)",
  "actor_evidence": [
    {
      "title": "근거 제목",
      "source": "출처명",
      "grade": "✅증거 | 🟡보통 | 🔍단서",
      "url": "원문 링크 (선택)",
      "ts": "타임스탬프"
    }
  ],
  "actor_confidence": 0, // 0~100
  "actor_tag": "수혜 | 피해 | 병목 | 회피 | 대체"
}
```

## 2. Actor 도출 로직 (Bridge Logic)

### 2.1 매핑 규칙 (Rule-based)

| 매크로 신호 | 1순위 후보 Actor | 성격 (Tag) |
| :--- | :--- | :--- |
| **금리/물가** (CPI, PCE, US10Y) | 미국 장기채 / 달러 | 회피 / 대체 |
| **에너지** (WTI, Brent) | 에너지 섹터 | 수혜 |
| **지정학** (전쟁, 봉쇄) | 방산 섹터 / 해운 섹터 | 수혜 |
| **기업 공시** (8-K, Filing) | 해당 기업 | 병목 / 대체 |

### 2.2 신뢰도 점수 (Evidence Scoring)

- **기본 점수**: 50점
- **HARD_FACT 포함**: +20점
- **MEDIUM_FACT 포함**: +10점
- **TEXT_HINT 포함**: +3점
- **Why-Now 일치**: +10점
- **최종 점수 70점 미만 시**: `actor_type="없음"` 처리 (EDITORIAL 승격 방지)

## 3. UI 렌더링 규칙 (한글 100%)

- **배지 표기**:
  - ✅ **증거** (HARD_FACT)
  - 🟡 **보통** (MEDIUM)
  - 🔍 **단서** (TEXT_HINT)
- **표시 위치**:
  - `EDITORIAL VIEW` (상단): 주인공 라인 및 근거 요약 상시 노출.
  - `SPEAKABLE` (리스트): 🏷️ **주인공 있음** / **주인공 없음** 아이콘 표시.

## 4. 헌법 준수 (Safety)

1. 근거 없는 강제 승격 금지: `actor_evidence`가 비어있으면 주체를 선정하지 않는다.
2. 실데이터 우선: `data/facts/`에 존재하는 실제 데이터만을 근거로 사용한다.
