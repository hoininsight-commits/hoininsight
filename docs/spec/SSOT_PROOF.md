# SSOT Proof of Authority

이 문서는 프로젝트의 Publisher 레이어에 대한 SSOT(Single Source of Truth)를 증거 기반으로 확정합니다.

## 1. 확정된 SSOT 경로
**SSOT Publisher Path = src/ui/run_publish_ui_decision_assets.py**

이 경로는 `.github/workflows/full_pipeline.yml`에서 최종 배포 직전에 실제로 실행되는 유일한 퍼블리싱 엔트리포인트입니다.

## 2. 증거 데이터 (Evidence)

### A. 파일 정보 (Identity)
- **File Path**: `src/ui/run_publish_ui_decision_assets.py`
- **SHA-1 Hash**: `5a49259c9a5f10bd869d0242d4719fe01ab195a7`
- **File Status**: 
  ```text
  -rw-r--r--@ 1 jihopa  staff  17930  2 26 18:01 src/ui/run_publish_ui_decision_assets.py
  ```

### B. CI/CD 실행 증거 (Pipeline Logic)
`.github/workflows/full_pipeline.yml:L373-378`
```yaml
# [IS-100] Generate manifest + Publish UI Decision Assets
echo "[PUBLISH] Using publish SSOT: src/ui/run_publish_ui_decision_assets.py"
echo "[PUBLISH] Publish SSOT path details:"
ls -al src/ui/run_publish_ui_decision_assets.py
python -m src.ui.run_publish_ui_decision_assets
```

### C. 생성된 결과물 (Manifest Sample)
`docs/data/decision/manifest.json` (Head 20 lines):
```json
{
  "generated_at": "2026-02-26T23:37:24.778511",
  "files": [
    "tone_persona_lock.json",
    "today.json",
    "speakability_decision.json",
    "script_with_citation_guard.json",
    "script_realization.json",
    "relationship_stress.json",
    "natural_language_briefing.json",
    "narrative_skeleton.json",
    "multi_topic_priority.json",
    "mentionables.json",
    "interpretation_units.json",
    "final_decision_cards/TEST-LOCKED-001.json",
    "evidence_citations.json",
    "editorial/editorial_selection_2026-02-26.json",
    "editorial/editorial_selection_2026-02-25.json",
    "editorial/editorial_selection_2026-02-24.json",
    "editorial/editorial_selection_2026-02-23.json",
```

---
*이후 모든 구조 작업 및 리팩토링은 위 SSOT 파일을 절대 기준으로 삼아 진행하며, 중복된 다른 구현체는 이 파일을 가리키는 Shim으로 대체합니다.*
