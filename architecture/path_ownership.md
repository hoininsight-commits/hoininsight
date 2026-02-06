# HoinInsight Path Ownership Manifest

이 문서는 프로젝트 내 각 디렉토리의 역할과 소유권을 정의합니다. (REF-006)

| 경로 | 역할 | 쓰기 권한 (Logic) | 비고 |
| :--- | :--- | :---: | :--- |
| `src/engine/` | 엔진/판단/수집 로직 | ✅ | 파이프라인 본체 |
| `src/ui_logic/` | UI 로직/계약/카드 빌더 | ✅ | **Single Source of Truth** |
| `src/ui/` | 레거시 호환 레이어 | ❌ | Shim (Alias) 전용 |
| `src/view/` | UI 렌더링 (순수 View) | ❌ | JSON 데이터 소비만 수행 |
| `data_outputs/` | 운영 중심 데이터 | ✅ | **운영 기준 데이터 (SSOT)** |
| `data/` | 개발 로컬 데이터 | ✅ | 로컬 개발용 호환 경로 |
| `docs/data/` | 배포용 데이터 | ✅ | GitHub Pages 배포용 복사본 |
| `registry/` | 정책/레지스트리/스키마 | ✅ | 설정 및 고정 규칙 |

---
**원칙**: 로직은 폴더 역할에 맞게 작성하고, 데이터는 `data_outputs/`를 최종 기준으로 삼는다.
