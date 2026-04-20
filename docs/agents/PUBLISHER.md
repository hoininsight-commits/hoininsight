# PUBLISHER 설계 원칙
v1.0 | 2026-04-20

## 역할
최종 분석 결과와 스크립트를 통합하여 웹 대시보드용 데이터를 생성하고, 과거 토픽 아카이브를 누적 관리한다.

## 입력 / 출력
- **입력**: `today_signal.json`, `today_analysis.json`, `today_script.md`, `signal_log.json`
- **출력**: `docs/data/today_data.json` (대시보드 소스), `docs/topics/index.json` (아카이브 인덱스)

## 핵심 로직
1. **Dashboard Data Assembly**: 대시보드 렌더링에 필요한 모든 필드(토픽, 내러티브, 종목 등)를 하나의 JSON으로 병합
2. **Archive Reconstruction**: `data/history/signal_log.json` 전체를 읽어 `docs/topics/index.json`을 매일 최신순으로 완벽히 재구성
3. **Date Normalization**: 8자리 숫자나 ISO 포맷 등 혼재된 날짜 형식을 `YYYY-MM-DD`로 통일
4. **Agent Status Update**: 파이프라인 수행 결과(`pipeline_results.json`)를 대시보드 상태창에 실시간 반영

## 수정 시 주의사항
- `index.json` 갱신 시 누락되는 과거 데이터가 없도록 `signal_log.json`을 Full-scan 할 것
- 대시보드 UI 테마(Amber Terminal)와 데이터 필드 간 호환성 유지

## 알려진 이슈
- 대규모 아카이브 누적 시 `index.json` 파일 크기 최적화 필요성 제기됨
