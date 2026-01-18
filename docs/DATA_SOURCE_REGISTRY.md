# DATA_SOURCE_REGISTRY

VERSION: v1.0
DATE: 2026-01-18
PURPOSE: 새로운 데이터 수집 필요성 발견 시, 자동으로 데이터 소스를 매칭하고 수집 모듈을 생성하기 위한 레지스트리

---

## 운영 원칙

1. **데이터 필요성 감지 → 소스 매칭 → 수집 모듈 자동 생성**
2. 기존 DATA_COLLECTION_MASTER에 없는 데이터만 처리
3. 무료 우선, 유료는 명시적 승인 필요
4. 모든 신규 데이터는 CANDIDATE 상태로 시작

---

## 데이터 소스 카테고리별 매칭 규칙

### 1. 국내 주식 시장 데이터

| 데이터 유형 | 추천 소스 | API/방식 | 무료 여부 | 수집 주기 |
|---|---|---|---|---|
| 외국인/기관 수급 | KRX 정보데이터시스템 | CSV/공개 | Free | 1일 |
| 연기금 매매 동향 | 금융감독원 전자공시 | DART API | Free | 1주 |
| 섹터별 ETF 거래대금 | KRX ETF 시장 | CSV | Free | 1일 |
| 밸류업 참여 기업 | 금융위원회 공시 | 공개자료 | Free | 이벤트 |
| 개별 종목 거래대금 | KRX | CSV | Free | 1일 |

### 2. 글로벌 기업 데이터

| 데이터 유형 | 추천 소스 | API/방식 | 무료 여부 | 수집 주기 |
|---|---|---|---|---|
| 테슬라 FSD 주행 데이터 | Tesla Investor Relations | 웹스크래핑/공시 | Free | 분기 |
| 빅테크 CAPEX | SEC EDGAR | API | Free | 분기 |
| AI 인프라 투자 | 기업 IR 자료 | 웹스크래핑 | Free | 분기 |

### 3. 정책/정부 데이터

| 데이터 유형 | 추천 소스 | API/방식 | 무료 여부 | 수집 주기 |
|---|---|---|---|---|
| 정부 예산 집행률 | 열린재정 | API | Free | 1개월 |
| 정부 발주/계약 | 나라장터 | API | Free | 1주 |
| 정책 발표 일정 | 정부 공식 사이트 | RSS/웹스크래핑 | Free | 1일 |

### 4. 산업/인프라 데이터

| 데이터 유형 | 추천 소스 | API/방식 | 무료 여부 | 수집 주기 |
|---|---|---|---|---|
| 전력망 가동률 | 전력거래소 | 공개자료 | Free | 1주 |
| 데이터센터 용량 | 산업 리포트 | 웹스크래핑 | Free | 1개월 |
| 반도체 장비 수주 | 기업 공시 | DART | Free | 분기 |

---

## 자동 매칭 알고리즘

### Step 1: 키워드 추출
Evolution Proposal의 `condition` 필드에서 핵심 키워드 추출
- 예: "외국인 수급" → ["외국인", "수급", "매매"]

### Step 2: 소스 매칭
- 키워드를 DATA_SOURCE_REGISTRY와 매칭
- 매칭 점수 계산 (키워드 일치도 + 카테고리 유사도)
- 상위 3개 후보 소스 제시

### Step 3: 수집 모듈 생성 제안
- 템플릿 기반 Python 스크립트 자동 생성
- `src/collectors/auto_generated/` 디렉토리에 저장
- 사용자 승인 후 활성화

---

## 수집 모듈 템플릿 구조

```python
# src/collectors/auto_generated/collect_{data_name}.py
"""
Auto-generated collector for: {data_name}
Source: {source_name}
Generated: {timestamp}
Status: CANDIDATE
"""

from pathlib import Path
import json
from datetime import datetime

def collect():
    """Collect {data_name} from {source_name}"""
    # TODO: Implement collection logic
    # 1. Fetch data from source
    # 2. Parse and validate
    # 3. Save to data/raw/{category}/{data_name}/
    pass

if __name__ == "__main__":
    collect()
```

---

## 승인 프로세스

1. **자동 감지**: Deep Logic Analyzer가 데이터 필요성 감지
2. **소스 매칭**: DATA_SOURCE_REGISTRY에서 최적 소스 찾기
3. **모듈 생성**: 템플릿 기반 수집 스크립트 자동 생성
4. **대시보드 표시**: "시스템 진화 제안"에 표시
5. **사용자 승인**: 승인 시 수집 모듈 활성화 + DATA_COLLECTION_MASTER 업데이트
6. **자동 실행**: GitHub Actions에 수집 스케줄 추가

---

## 예시: 외국인 수급 데이터 자동 추가

### 감지된 필요성
```json
{
  "id": "EVO-20260118-26886",
  "category": "DATA_ADD",
  "content": {
    "condition": "두 번째로 확인해야 할 건 외국인 수급 방향이야"
  }
}
```

### 자동 매칭 결과
- **데이터명**: 외국인/기관 매매 동향
- **소스**: KRX 정보데이터시스템
- **방식**: CSV 다운로드
- **주기**: 1일

### 생성될 모듈
- `src/collectors/auto_generated/collect_foreign_investor_flow.py`
- 저장 경로: `data/raw/market_flow/foreign_investor/YYYY/MM/DD/flow.csv`

---

## 다음 단계

1. ✅ DATA_SOURCE_REGISTRY 작성 (본 문서)
2. ⏳ Auto Collector Generator 구현
3. ⏳ 대시보드에 "데이터 소스 제안" 섹션 추가
4. ⏳ 승인 시 자동 활성화 로직 구현
