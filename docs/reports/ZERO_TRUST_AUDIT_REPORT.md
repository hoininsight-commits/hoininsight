# HOIN Insight Zero-Trust Audit Report (운영 서버 기준)

## 1. 감사 목적
본 보고서는 HOIN Insight 시스템의 신뢰성을 "제로 트러스트(Zero-Trust)" 관점에서 재검증하기 위해 작성되었습니다. 운영 서버(`https://hoininsight-commits.github.io/hoininsight/`)의 실제 배포 상태를 기준으로 데이터와 UI의 정합성을 대조하였습니다.

## 2. 감사 범위
- **UI 정합성**: 8개 핵심 화면 (Main, Radar, Brief, Impact, Studio, Today, System, Sidebar)
- **데이터 정합성**: 배포된 13종의 JSON 데이터 및 SSOT(`today_operator_brief.json`)
- **소스 정합성**: 배포 해시(`6baa728c...`) 기준 소스 스택

## 3. 운영 서버 기준 확인 방법
- **캡처**: 브라우저 자동화를 통해 실시간 운영 URL 화면 채득 (총 8종).
- **데이터 추출**: 서버의 `data/` 경로에서 직접 JSON 다운로드 및 분석.
- **소스 매핑**: 서버 `build_meta.json`의 커밋 해시를 로컬 소스와 비교.

## 4. 정합성 검증 결과 (Evidence-Based)

### A. 의미 정합성 (Semantic Consistency) - [FAIL]
서버 데이터(`today_operator_brief.json`) 분석 결과, 레이어 간 서사 불일치가 확인되었습니다.
- **Market Radar Theme**: `AI Power Constraint`
- **Narrative Brief Featured Theme**: `AI Evolution` (레이더 테마와 불일치)
- **Content Studio Topic**: `Policy Radar` (검출된 AI 테마와 맥락 없음)
- **증거**: `hoin_server_data_snapshot.zip/data_ops_today_operator_brief.json`

### B. 데이터 정합성 (Data Consistency) - [HOLD]
- **업데이트 지연**: 서버 데이터의 최종 생성 시점이 **2026-03-17**로, 감사 시점(03-24) 대비 7일간 업데이트가 중단된 상태입니다.
- **파일 누락**: `execution_log.json`, `performance_report.json` 등 핵심 사후 분석 파일이 운영 서버 경로에서 404로 나타납니다.
- **가짜 데이터**: 모든 종목의 Rationale이 "High relevance to Market Equilibrium"으로 고정되어 있어 엔진 분석값이 UI에 바인딩되지 않았음이 확인됩니다.

### C. UI 명확성 및 워크플로우 (UI/Workflow) - [HOLD]
- **Today 화면**: 7일 전 데이터를 "오늘의 선정"으로 표시하고 있어 운영상의 오정보 제공 위험이 있습니다.
- **Sidebar**: 전체 구조는 양호하나, 테마와 무관한 메뉴(Policy Radar 등)가 노출되어 일관성을 실해합니다.

## 5. 소스 구조 점검 결과
현재 수집된 소스 코드 검토 결과, `ConsistencyEngine`이 존재하지만 필드 간의 강제 동기화(Enforced Alignment) 로직이 특정 브랜치에서 누락되었거나 작동하지 않는 상태입니다.

## 6. 현재 시스템의 핵심 문제 5개
1. **서사 파편화**: 레이더(AI 전력)와 브리핑(AI 진화), 토픽(정책)이 각각 따로 노는 현상.
2. **배포 파이프라인 정체**: 3월 17일 이후 운영 서버로의 데이터 업데이트가 이루어지지 않음.
3. **핵심 데이터 누락**: 사후 분석 및 실행 로그 파일의 서버 퍼블리싱 로직 부재.
4. **플레이스홀더 고착**: 종목 분석 근거가 엔진 결과값으로 교체되지 않음.
5. **경로 표준화 미비**: `operator/`와 `ops/` 경로가 혼용되어 데이터 SSOT 관리가 어려움.

## 7. 즉시 수정 우선순위 (Top 5 Fixes)
1. **파이프라인 복구**: 03-17일자에서 멈춘 데이터 업데이트 자동화를 즉시 재개.
2. **ConsistencyEngine 강화**: `core_theme`를 기준으로 브리핑 테마와 토픽을 강제 치환하는 로직 구현.
3. **데이터 퍼블리셔 수정**: 404가 발생하는 3종 파일을 포함하여 16종 전체를 `data/ops/`로 출력.
4. **실제 데이터 바인딩**: 임팩트 맵의 Rationale 필드를 엔진 분석값으로 연결.
5. **UI 클린업**: 테마와 무관한 'Policy Radar' 등 불필요한 레이어 노출 제거.

## 8. 최종 판정: [HOLD]
**사유**: 데이터가 일주일간 정체되어 있으며, 테마 간 서사 불일치가 심각하여 운영 결정 도구로서의 신뢰성을 상실한 상태입니다. 상기 우선순위 조치 후 재검사가 필요합니다.

**작성자**: Antigravity Audit Bot
**날짜**: 2026-03-24
