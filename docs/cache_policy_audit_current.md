# Audit: Current Cache Policy — HOIN Insight (#080-TASK-1)

This document provides a comprehensive audit of all data sources within the HOIN Insight collection layer, mapping their current caching logic, frequency, and valid execution constraints.

## 📊 Data Source Audit Matrix

| 데이터 소스명 | 파일/모듈 경로 | 캐시 여부 | 캐시 방식 | TTL / 유지 조건 | 갱신 주기 (외부) | 수집 주기 | Cache Hit 기준 | Skip 조건 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FRED Macro** | `collector.py` | YES | 파일 (JSON) | 당일 (`/YYYYMMDD/`) | 주간/월간 | 일 1회 이상 | 파일 존재 및 >100B | `fred.json` 존재 |
| **ECOS Macro** | `collector.py` | YES | 파일 (JSON) | 당일 (`/YYYYMMDD/`) | 월간/분기 | 일 1회 이상 | 파일 존재 및 >100B | `ecos.json` 존재 |
| **RSS News** | `collector.py` | YES | 파일 (JSON) | 당일 (`/YYYYMMDD/`) | **실시간 (분)** | 일 1회 이상 | 파일 존재 및 >100B | `sentiment.json` 존재 |
| **Market Stats**| `collector.py` | YES | 파일 (JSON) | 당일 (`/YYYYMMDD/`) | **실시간 (초)** | 일 1회 이상 | 파일 존재 및 >100B | `market.json` 존재 |
| **DART 공시** | `collector.py` | YES | 파일 (JSON) | 당일 (`/YYYYMMDD/`) | 실시간 (분) | 일 1회 이상 | 파일 존재 및 >100B | `dart.json` 존재 |
| **COT Data** | `cot_collector.py`| YES | 파일 (JSON) | 당일 (`/YYYYMMDD/`) | 주간 (금요일) | 일 1회 이상 | 파일 존재 및 >100B | `cot.json` 존재 |
| **PutCall Ratio**| `putcall_coll.py`| YES | 파일 (JSON) | 당일 (`/YYYYMMDD/`) | 일간 | 일 1회 이상 | 파일 존재 및 >100B | `putcall.json` 존재 |
| **ETF Flow** | `flow_collector.py`| NO (Partial)| 파일 (Overwrite) | 없음 (덮어쓰기) | 일간 | 일 1회 이상 | N/A | 없음 |
| **Fear & Greed** | `collector.py` | NO | API 직접 호출 | N/A | 일간 | 일 1회 이상 | N/A | 없음 (매번 호출) |

## 🛠 캐시 메커니즘 상세

### 1. 전역 오케스트레이터 (`CollectorRunner`)
- **위치**: `src/agents/collectors/collector_runner.py`
- **로직**:
  ```python
  cache_file = self.output_dir / f"{agent_name.lower()}.json"
  if cache_enabled and cache_file.exists():
      if cache_file.stat().st_size > 100:
          # Cache Hit -> Skip Execution
  ```
- **특징**: `output_dir`이 날짜별 디렉토리(`data/raw/YYYYMMDD`)이므로, **하루에 한 번이라도 수집에 성공하면 해당 날짜의 추가 수집은 모두 차단됨.**

### 2. 특정 데이터 예외 처리
- **Fear & Greed**: API가 간단하고 볼륨이 작아 별도 캐시 로직 없이 매번 호출함.
- **ETF Flow**: `CollectorRunner`가 아닌 루틴 끝에 수동으로 실행되어 전역 캐시 로직의 영향을 받지 않음.

### 3. Cache Hit 시 데이터 Timestamp
- **현황**: 캐시된 파일(`sentiment.json` 등) 내부의 `collected_at` 필드가 생성 시점의 타임스탬프를 보존함.
- **문제**: 엔진은 이 타임스탬프가 "10시간 전"이어도 파일이 존재한다는 이유만으로 "신선한 것으로 간주"하고 넘어가게 됨.
