# 🤖 Antigravity Implementation Workflow

## 문제 인식

사용자님이 정확하게 지적하신 문제들:

1. ❌ **Antigravity가 구현할 때 참조할 제안 내용이 보관되지 않음**
2. ❌ **Deep Logic Analysis에 제안 상태가 표시되지 않음**
3. ❌ **마스터 문서(DATA_COLLECTION_MASTER, ANOMALY_DETECTION_LOGIC)가 업데이트되지 않음**
4. ❌ **구현된 내용과 문서 간 불일치**

---

## ✅ 해결 방안 (구현 완료)

### 1. 제안 보관 시스템

**위치:** `data/evolution/proposals/EVO-*.json`

**내용:**
```json
{
  "id": "EVO-20260118-26886",
  "category": "DATA_ADD",
  "status": "COLLECTOR_GENERATED",
  "content": {
    "condition": "외국인 수급 방향 확인 필요",
    "meaning": "Pattern: User explicit need"
  },
  "evidence": {
    "quote": "두 번째로 확인해야 할 건 외국인 수급 방향이야",
    "source": "한국 정부가 '코스닥'은 버리고 '코스피'만 밀어주는 진짜 이유"
  },
  "collector_script": "src/collectors/auto_generated/collect_foreign_investor_flow.py"
}
```

**Antigravity가 볼 수 있는 정보:**
- ✅ 제안 ID
- ✅ 카테고리 (DATA_ADD / LOGIC_UPDATE)
- ✅ 상태 (PROPOSED / COLLECTOR_GENERATED / APPROVED / INTEGRATED)
- ✅ 조건 및 의미
- ✅ 증거 (출처 영상)
- ✅ 생성된 수집 모듈 경로

---

### 2. 문서 동기화 시스템

#### A. 동기화 체커 (`doc_sync_checker.py`)

**실행:**
```bash
python3 -m src.evolution.doc_sync_checker
```

**출력:**
```
============================================================
📋 DOCUMENTATION SYNC REPORT
============================================================

📊 DATA COLLECTION:
  master_items_count: 59
  implemented_collectors: 3
  pending_proposals: 6
  sync_status: OK

🧠 ANOMALY LOGIC:
  documented_patterns: 9
  pending_logic_proposals: 16
  sync_status: NEEDS_REVIEW

💡 RECOMMENDATIONS:
  ⚠️ 6 data proposals pending integration
  ⚠️ 16 logic proposals pending integration
```

#### B. 제안 통합기 (`proposal_integrator.py`)

**기능:**
- 승인된 제안을 DATA_COLLECTION_MASTER.md에 자동 추가
- 승인된 로직을 ANOMALY_DETECTION_LOGIC.md에 자동 추가
- 백업 파일 생성 (.md.backup)
- 제안 상태를 INTEGRATED로 변경

**실행:**
```bash
python3 -m src.evolution.proposal_integrator
```

---

### 3. Deep Logic Analysis 통합

**현재 상태:**
- ✅ 제안이 `evolution_proposals` 필드에 포함됨
- ✅ 제안 상태 추적 (`_enrich_proposals_with_status`)
- ⏳ 대시보드 표시 (다음 단계)

---

## 🔄 완전한 워크플로우

```
1. 영상 분석 (자동)
   ↓
2. Deep Logic Analyzer가 제안 생성
   → data/evolution/proposals/EVO-*.json 저장
   ↓
3. Auto Collector Generator 실행
   → src/collectors/auto_generated/collect_*.py 생성
   ↓
4. Human Loop Notifier 실행
   → Telegram 알림 + GitHub Issue 생성
   ↓
5. 사용자 대시보드 검토
   ↓
6. 🤖 Antigravity 요청 버튼 클릭
   ↓
7. GitHub Issue 생성
   "제안 ID: EVO-20260118-26886
    조건: 외국인 수급 방향 확인 필요
    수집 모듈: collect_foreign_investor_flow.py
    상태: 템플릿 생성 완료, API 연동 필요"
   ↓
8. 사용자가 Antigravity에게 알림:
   "GitHub Issues 확인해줘. EVO-20260118-26886 구현 필요해"
   ↓
9. Antigravity 작업 시작:
   
   A. 제안 파일 확인
   $ cat data/evolution/proposals/EVO-20260118-26886.json
   
   B. 동기화 상태 확인
   $ python3 -m src.evolution.doc_sync_checker
   
   C. 수집 모듈 완성
   - KRX API 연동
   - 데이터 검증 로직
   - 테스트 실행
   
   D. 문서 업데이트
   $ python3 -m src.evolution.proposal_integrator
   → DATA_COLLECTION_MASTER.md 자동 업데이트
   
   E. 제안 상태 변경
   status: COLLECTOR_GENERATED → INTEGRATED
   
   F. Pull Request 생성
   ↓
10. 자동 배포
    → GitHub Actions에서 매일 실행
    → 데이터 자동 수집
```

---

## 📋 Antigravity 체크리스트

### 구현 시작 전

- [ ] GitHub Issue 확인
- [ ] 제안 파일 확인 (`data/evolution/proposals/EVO-*.json`)
- [ ] 동기화 상태 확인 (`doc_sync_checker.py`)
- [ ] 기존 수집 모듈 템플릿 확인

### 구현 중

- [ ] API 연동 완성
- [ ] 데이터 검증 로직 추가
- [ ] 테스트 실행 (로컬)
- [ ] 에러 처리 추가

### 구현 완료 후

- [ ] `proposal_integrator.py` 실행
- [ ] DATA_COLLECTION_MASTER.md 업데이트 확인
- [ ] ANOMALY_DETECTION_LOGIC.md 업데이트 확인 (로직 제안인 경우)
- [ ] 제안 상태 → INTEGRATED 확인
- [ ] Pull Request 생성
- [ ] GitHub Issue 종료

---

## 📊 현재 상태 (2026-01-18)

### 대기 중인 제안

**데이터 수집 (6건):**
1. EVO-20260118-26886 - 외국인 수급 방향
2. EVO-20260118-14701 - 연기금 스탠스
3. EVO-20260118-95759 - 밸류업 참여 기업
4. EVO-20260118-50129 - 유동성/실적 장세 판별
5. EVO-20260118-53189 - 테슬라 FSD 데이터
6. EVO-20260118-11958 - (기타)

**로직 업데이트 (16건):**
- 대부분 1월 17-18일 영상 분석에서 생성됨
- 정부 정책, 구조적 변화, 자본 이동 관련

### 수집 모듈 상태

**생성 완료 (3개):**
- ✅ `collect_foreign_investor_flow.py` - 템플릿
- ✅ `collect_pension_fund_flow.py` - 템플릿
- ✅ `collect_value_up_participants.py` - 템플릿

**구현 필요:**
- ⏳ KRX API 실제 연동
- ⏳ DART API 연동
- ⏳ 데이터 검증 로직
- ⏳ 에러 처리

---

## 🎯 다음 단계

### 사용자님이 할 일:

1. **대시보드 확인**
   - https://hoininsight-commits.github.io/hoininsight/
   - "시스템 진화 제안" 탭

2. **제안 검토**
   - 6개 데이터 제안
   - 16개 로직 제안

3. **Antigravity 요청**
   - 🤖 버튼 클릭
   - 추가 요구사항 입력 (선택)

4. **Antigravity에게 알림**
   ```
   "GitHub Issues에 새로운 구현 요청이 있어.
   EVO-20260118-26886부터 시작해서
   6개 데이터 수집 모듈을 완성해줘.
   
   우선순위:
   1. 외국인 수급 (KRX API)
   2. 연기금 매매 (KRX API)
   3. 밸류업 참여 기업 (금융위 공시)"
   ```

### Antigravity가 할 일:

1. **제안 파일 확인**
2. **동기화 상태 확인**
3. **수집 모듈 완성**
4. **문서 업데이트**
5. **테스트 및 검증**
6. **Pull Request 생성**

---

## 📁 파일 구조

```
HoinInsight/
├── data/
│   └── evolution/
│       ├── proposals/          # 제안 보관소 (Antigravity가 참조)
│       │   ├── EVO-20260118-26886.json
│       │   └── ...
│       ├── notifications/      # 알림 이력
│       └── sync_report.json    # 동기화 리포트
│
├── docs/
│   ├── DATA_COLLECTION_MASTER.md      # 데이터 마스터 (업데이트 대상)
│   ├── ANOMALY_DETECTION_LOGIC.md     # 로직 마스터 (업데이트 대상)
│   ├── BASELINE_SIGNALS.md            # 기준정보 마스터
│   └── HUMAN_LOOP_WORKFLOW.md         # 워크플로우 가이드
│
├── src/
│   ├── collectors/
│   │   └── auto_generated/     # 자동 생성 수집 모듈
│   │       ├── collect_foreign_investor_flow.py
│   │       ├── collect_pension_fund_flow.py
│   │       └── collect_value_up_participants.py
│   │
│   └── evolution/
│       ├── human_loop_notifier.py     # 알림 시스템
│       ├── proposal_integrator.py     # 문서 통합기
│       └── doc_sync_checker.py        # 동기화 체커
│
└── .github/workflows/
    └── full_pipeline.yml       # 자동화 파이프라인
```

---

## ✅ 요약

**문제:**
- Antigravity가 구현할 때 참조할 정보 부족
- 문서와 구현 불일치

**해결:**
- ✅ 제안을 JSON 파일로 보관 (`data/evolution/proposals/`)
- ✅ 동기화 체커로 불일치 감지 (`doc_sync_checker.py`)
- ✅ 자동 통합기로 문서 업데이트 (`proposal_integrator.py`)
- ✅ Human-in-the-Loop 워크플로우 구축

**결과:**
- 🎯 Antigravity가 제안 파일만 보면 모든 정보 확인 가능
- 🎯 문서 자동 업데이트로 일관성 유지
- 🎯 사용자는 버튼 하나만 클릭하면 됨
