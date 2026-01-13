# Add Dataset Guide (Hoin Insight)

본 가이드는 신규 데이터셋을 **Additive(누적)** 방식으로 안전하게 추가하기 위한 표준 절차다.

## 1) Registry에 데이터셋 추가
`registry/datasets.yml`의 datasets 배열에 아래 필드를 포함한 블록을 추가한다.

필수 필드:
- dataset_id: 고유 ID (예: macro_us_fed_funds_fred)
- enabled: true/false
- entity: 관측 대상 식별자 (예: BTCUSD, USDKRW)
- unit: 단위 (예: USD, KRW, %)
- source: 원천 (예: coingecko)
- metric_name: 지표명 (예: spot_price, rate)
- schema_version: 스키마 버전 (현재 timeseries_v1)
- collector: "module.path:function"
- normalizer: "module.path:function"
- anomaly: "module.path:function"
- topic: "module.path:function"
- report_key: 리포트 섹션 키
- curated_path: curated csv 경로 (예: data/curated/xxx/yyy.csv)

## 2) Collector 작성 규칙
- raw 파일은 아래 규칙 경로에 저장한다:
  - data/raw/{source}/YYYY/MM/DD/{name}.json
- raw에는 최소한 다음 키를 포함한다:
  - ts_utc, source, entity, unit, (value 필드)

## 3) Normalizer 작성 규칙
- curated는 반드시 timeseries_v1 스키마를 만족해야 한다:
  - ts_utc, entity, value, unit, source, dataset_id, metric_name, is_derived, derived_from, fingerprint
- fingerprint는 공통 유틸(make_fingerprint)을 사용한다.
- append_timeseries_csv를 사용하여 중복 제거(keep last)를 강제한다.

## 4) Derived Metrics 규칙
- 파생 지표는 is_derived=true
- derived_from에는 원본 dataset_id를 명시한다(빈 문자열 금지)

## 5) 검증(Quality Gate)
- output_check: curated/anomalies/topics/report 존재 여부 확인
- schema_check: curated csv가 schema_version에 맞는지 확인
- 실패 시: 엔진 FAIL + run_log/health 기록 + (Actions) Issue 생성

## 6) 실행
로컬:
- python -m src.engine

GitHub Actions:
- workflow_dispatch로 full_pipeline 실행
