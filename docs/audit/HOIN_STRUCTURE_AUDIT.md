# HOIN Insight 시스템 구조 감사 보고서
v1.0 | 2026-04-20 감사 수행

## A. 레포 전체 구조 파악

### A-1. 주요 디렉토리 구조
| 디렉토리 | 용도 | 실제 사용 여부 | 비고 |
| :--- | :--- | :--- | :--- |
| `src/` | 에이전트, 코어 로직, 유틸리티 소스코드 | **Active** | 모든 실행 로직 포함 |
| `data/` | 수집 데이터, 신호, 분석, 기록 저장 | **Active** | 파이프라인 중간/최종 산출물 저장소 |
| `docs/` | GitHub Pages 웹 서비스 및 명세서 보관 | **Active** | 대시보드 배포 및 방대한 설계 문서 풀 |
| `config/` | 시스템 설정 및 필터 정의 | **Active** | JSON/YAML 설정 파일 |
| `.github/` | CI/CD (GitHub Actions) 설정 | **Active** | `daily_pipeline.yml`이 메인 엔진 |
| `dashboard/` | 대시보드 UI 소스 (HTML/JS) | **Active** | `publish` 시 `docs/`로 동기화됨 |
| `scripts/` | 과거 생성된 시나리오/스크립트 저장소 | **Legacy** | 현재는 `data/scripts/` 위주 사용 |

### A-2. 핵심 실행 진입점 (Entry Points)
실제 파이프라인 및 로직의 시작점은 다음과 같습니다.

| 실행 범위 | 진입점 파일 경로 | 핵심 함수/명령어 | 실제 사용 여부 |
| :--- | :--- | :--- | :--- |
| **전체 파이프라인** | `.github/workflows/daily_pipeline.yml` | `workflow_dispatch` 또는 `schedule` | **Active** |
| **데이터 수집** | `src/agents/collectors/collector_runner.py` | `CollectorRunner.run_all()` | **Active** |
| **이상징후 탐지** | `src/agents/detector.py` | `DetectorAgent.run()` | **Active** |
| **심층 분석** | `src/agents/analyst.py` | `AnalystAgent.run()` | **Active** |
| **스크립트 생성** | `src/agents/writer.py` | `WriterAgent.run()` | **Active** |
| **최종 발행** | `src/agents/publisher.py` | `PublisherAgent.run()` | **Active** |

---

## B. 파이프라인 단계 (Logical Stages)

코드 및 워크플로우 분석 결과, 현재 시스템은 추정이 아닌 **실제 4단계 잡(Job)**으로 구성되어 동작합니다.

1.  **COLLECT (수집)**: 전 세계 API 및 매크로 지표를 `data/raw/`에 JSON 형식으로 규격화하여 저장.
2.  **INTELLIGENCE (지능)**: 
    - **Detector**: 통계적 이상징후 탐지 및 '오늘의 신호' 선정.
    - **Analyst**: 선정된 신호의 메커니즘 분석 및 종목 브리지 형성.
3.  **WRITE (집필)**: 
    - **Writer**: '경제사냥꾼' 7단계 빌드업 기반 유튜브 스크립트 작성.
    - **Fact-Checker**: 스크립트 내 수치의 무결성 검증.
4.  **PUBLISH (발행)**: 
    - **Publisher**: 대시보드용 데이터(`/docs/today_data.json`) 갱신 및 아카이브 누적.

---

## C. 감사 총평
현재 시스템은 **데이터 기반의 철저한 SSOT(Single Source of Truth) 체계**를 유지하고 있습니다. 모든 에이전트가 `data/` 하위의 JSON을 읽고 쓰며, 최종적으로 `docs/` 경로를 통해 사용자에게 노출되는 구조입니다. 특히 `3계층 문장 관리`와 `Fact-Checker`를 통해 AI의 환각을 기술적으로 억제하고 있음이 확인되었습니다.
