# Design: Freshness Metadata — HOIN Insight (#080-TASK-5)

This document defines the metadata structure to be embedded in all collected data files, enabling the engine to assess data reliability and freshness.

## 📋 Freshness Metadata Schema

모든 `.json` 데이터 파일의 최상위 레벨에 아래 필드를 포함하도록 설계한다:

```json
{
  "metadata": {
    "collected_at": "ISO8601 Timestamp",    // 실제 수집 시점
    "source_timestamp": "ISO8601 Timestamp", // 외부 소스가 제공하는 데이터 생성 시각 (제공 시)
    "cache_hit": boolean,                   // 캐시에서 가져왔는지 여부
    "ttl_policy_minutes": integer,          // 해당 데이터에 적용된 TTL 정책
    "freshness_status": "StatusEnum",       // [FRESH, STALE, UNKNOWN]
    "provider": "string"                    // 데이터 공급자 (FRED, Yahoo, etc.)
  },
  "data": { ... }
}
```

### 1. 필드별 상세 정의
- **collected_at**: Python의 `datetime.now().isoformat()` 값.
- **source_timestamp**: Yahoo Chart나 ECOS API에서 주는 `latest_date` 등을 ISO 형식으로 변환. 데이터 소스의 시간과 수집 시간의 격차를 추적함.
- **freshness_status**:
    - `FRESH`: `datetime.now() - collected_at` < `ttl_policy_minutes`
    - `STALE`: `datetime.now() - collected_at` >= `ttl_policy_minutes`
    - `UNKNOWN`: 수집 파이프라인 장애로 상태 확인 불가

## 🔄 메타데이터 생성 흐름 (Generator)

1. **`CollectorAgent` 메서드**: 각 `_get_xxx` 메서드가 성공적으로 종료될 때, 위 스키마에 맞춰 딕셔너리를 구성함.
2. **`CollectorRunner`**: 캐시를 읽어올 때 `cache_hit: true`를 주입하고, `freshness_status`를 현재 시간 기준으로 재계산하여 업데이트함.
3. **`SanityCheck`**: 주기적으로 이 메타데이터를 검사해 `STALE` 비율이 높으면 경고 알림을 발송함.

## 🧠 엔진 활용 로직 (Consumption)

### DetectorAgent (탐지 단계)
- `freshness_status == STALE`인 데이터에서 발생한 시그널은 **신뢰도 가중치(Confidence Weight)**를 30% 감점함.
- "어제 뉴스"로 오늘을 판단하지 않도록 필터링.

### AnalystAgent (분석 단계)
- 데이터가 Stale할 경우, 내러티브 생성 시 "주의: 지연된 데이터를 기반으로 분석됨" 문구를 자동 삽입.
- `source_timestamp`와 `collected_at`의 차이가 24시간 이상일 경우 '심각' 단계로 분류.

## 🚀 기대 효과
1. **투명성**: 엔진이 "왜 이 시그널을 변두리로 밀어냈는가?"에 대한 데이터적 근거 제공.
2. **비용 효율**: 실시간 데이터(HIGH)와 정적 데이터(LOW)를 메타데이터 기반으로 차별화 관리 가능.
3. **시스템 건전성**: 수집 장애 상황을 데이터 레벨에서 즉각 감지.
