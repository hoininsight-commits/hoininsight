# Runtime Entrypoints (Allow List)

이 문서는 프로젝트 런타임(`full_pipeline.yml`)에서 실제로 호출되는 엔트리포인트 목록입니다. 이 목록에 없는 파일 중 런타임에 기여하지 않는 파일은 Phase 20의 격리 대상이 됩니다.

## 1. Core Services (python -m)

| Module Path | Layer | Purpose |
| :--- | :--- | :--- |
| `src.engine` | Engine | Core sensing & analysis logic |
| `src.issuesignal.run_issuesignal` | Ops | Issue detection & analysis |
| `src.ops.narrative_intelligence_layer` | Ops | Narrative generation & selection |
| `src.ops.video_intelligence_layer` | Ops | Video candidate selection |
| `src.ui.run_publish_ui_decision_assets` | Publisher | **SSOT** Asset publishing & manifesting |
| `src.dashboard.dashboard_generator` | Reporter | HTML/Markdown report generation |
| `src.reporting.telegram_daily_summary` | Reporter | Notification delivery |

## 2. Specialized Collectors

- `src.collectors.coingecko_collector`
- `src.collectors.ecos_collector`
- `src.collectors.fred_collector`
- `src.collectors.market_collectors`
- `src.collectors.policy_collector`

## 3. Support & Governance

- `src.ops.新鮮度追踪 (Freshness)`
- `src.ops.health_check`
- `src.ops.production_sanity_check`
- `src.pipeline.run_topic_gate`
- `src.topics.topic_candidate_gate`

---
*Note: 모든 신규 기능은 위 레이어 구조에 맞춰 추가되어야 하며, `docs/spec/SSOT_PROOF.md`의 원칙을 준수해야 합니다.*
