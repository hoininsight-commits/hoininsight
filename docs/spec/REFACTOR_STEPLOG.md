# Refactor Step Log (Phase 19B)

이 문서는 Phase 19B에서 수행된 물리적 구조 정리 및 무결성 조치 내역을 기록합니다.

## 1. 주요 변경 사항

| 영역 | 변경 파일 | 작업 내용 | 사유 |
| :--- | :--- | :--- | :--- |
| **SSOT Proof** | `docs/spec/SSOT_PROOF.md` | Publisher SSOT 명시적 확정 | 배포 권한 단일화 |
| **No-Dup Shim** | `src/ui/publish_ui_assets.py` | Implementation -> Shim 전환 | 중복 로직 제거 및 SSOT 참조 |
| **No-Dup Shim** | `src/ui_logic/contracts/run_publish_ui_decision_assets.py` | Shim 형식 표준화 | CI Guard 호환성 확보 |
| **Scoring Integrity** | `src/ui/run_publish_ui_decision_assets.py` | Salt 기반 더미 점수 생성 로직 제거 | 데이터 무결성 확보 (Fake Score 금지) |
| **Scoring Integrity** | `src/reporters/daily_report.py` | Reporter 레이어의 점수 보정 로직 제거 | Logic Leak 차단 및 원본 점수 유지 |
| **Legacy Archive** | `docs/legacy/` -> `archive/legacy_ui/` | 물리적 이동 (git mv) | 구형 자산 격리 |
| **Legacy Archive** | `docs/legacy/index.html` | 리다이렉트 안내 페이지 생성 | 사용자 경로 안내 |
| **Legacy Archive** | `docs/ui/*.js`, `docs/index.html` | Legacy 관련 코드/경로/주석 제거 | CI Guard 통과 및 동선 차단 |

## 2. 검증 결과 (Verification Log)

### A. CI Guard: Duplication Lock
- **Command**: `python3 scripts/verify_no_duplicate_publishers.py`
- **Result**: `✅ [OK] Verified 1 Implementation and 1 Shim(s)` per publisher pattern.

### B. CI Guard: Legacy Link Lock
- **Command**: `python3 scripts/verify_no_legacy_links.py`
- **Result**: `✅ [OK] No legacy links detected in target files.`

### C. Data Integrity: Null Contract
- **Test**: Local publisher execution (`src.ui.run_publish_ui_decision_assets`).
- **Evidence**: `narrative_score` 및 `actor_tier_score`가 존재하지 않는 샘플에서 `null` 값 확인 완료.

## 3. 원격 검증 (GitHub Actions/Pages)
- `full_pipeline.yml`에서 `SSOT_PROOF.md`에 정의된 핵심 퍼블리셔(`src.ui.run_publish_ui_decision_assets`)가 정상 작동함을 확인.
- 메인 대시보드에서 더 이상 구형 대시보드(Legacy)로 연결되는 링크가 존재하지 않음.

---
*Next: [STRUCTURE] Full Architecture Audit & Refactor Plan (Pre-Agent Modularization) 커밋 대기 중.*
