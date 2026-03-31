# New Project Structure Tree (Refactor Target)

이 구조는 모듈 버전 관리 및 Agent 기반 자동화를 위해 제안된 최종 구조입니다.

```text
HoinInsight/
 ├── src/
 │    ├── engine/             # [B] 핵심 연산 및 이상징후 탐지
 │    │    ├── core/          # 정규화, 기초 점수 산정
 │    │    ├── scoring/       # 모든 점수 보정 공식 (Persistence, Momentum 등)
 │    │    └── detectors/     # Anomaly/Signal 탐지 로직
 │    ├── ops/                # [C] 지능형 판단 확장 레이어
 │    │    ├── intelligence/  # Narrative, Video, Conflict
 │    │    ├── automation/    # Handoff, Bridge
 │    │    └── diagnostics/   # Forensics 트래킹
 │    ├── publisher/          # [D] SSOT 배포 레이어
 │    │    ├── core.py        # 배포 총괄 (기존 run_publish_ui_decision_assets.py)
 │    │    └── contracts/     # JSON Schema 및 계약 문서
 │    ├── collectors/         # [A] 외부 데이터 수집 통합
 │    └── utils/              # 하위 호환 유틸리티
 ├── docs/                    # [E] UI 및 운영 문서
 │    ├── ui/                 # 렌더링 프론트엔드
 │    ├── data/               # 배포된 SSOT 데이터 (Runtime)
 │    └── spec/               # 설계 사양서 (.md)
 ├── archive/                 # [F] 격리된 자산
 │    ├── legacy_ui/          # 구형 대시보드
 │    ├── forensics/          # 과거 Phase 분석 리포트
 │    └── experimental/       # 사용되지 않는 스크립트
 └── tests/                   # 검증 스크립트 모음
```

## 주요 개선점
1. **SSOT 가시성 확보**: `src/publisher`를 독립 모듈로 승격시켜 데이터 흐름의 투명성을 높임.
2. **계산 로직 중앙화**: `src/engine/scoring`에서 모든 보정 수식을 관리하여 리포터나 퍼블리셔의 로직 유출 방지.
3. **Legacy 격리**: `archive/` 폴더 도입으로 `src/`와 `docs/`의 순수도 유지.
4. **Agent 친화적 구조**: 모듈별 SRP(단일 책임 원칙) 분리로 AI 에이전트가 특정 기능 수정 시 부수 효과를 최소화함.
