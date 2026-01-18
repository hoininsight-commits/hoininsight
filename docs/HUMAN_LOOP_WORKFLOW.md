# Human-in-the-Loop Workflow Guide

## 개요

HOIN ENGINE이 유튜브 영상을 통해 학습하고 새로운 데이터 수집이나 로직 수정이 필요할 때, 자동으로 사용자에게 알림을 보내고 Antigravity에게 구현을 요청할 수 있는 시스템입니다.

---

## 🔄 전체 워크플로우

```
1. 영상 분석 (자동)
   ↓
2. 데이터/로직 필요성 감지 (자동)
   ↓
3. Evolution Proposal 생성 (자동)
   ↓
4. 수집 모듈 템플릿 생성 (자동)
   ↓
5. 📱 Telegram 알림 발송 (자동)
   ↓
6. 📋 GitHub Issue 생성 (자동)
   ↓
7. 👤 사용자 대시보드 검토
   ↓
8. 🤖 Antigravity 구현 요청 (버튼 클릭)
   ↓
9. ✅ Antigravity가 구현 완료
   ↓
10. 🚀 자동 배포 및 운영
```

---

## 📱 알림 채널

### 1. Telegram 알림

**발송 시점:** 매일 파이프라인 실행 시 (한국시간 08:00)

**알림 내용:**
```
🔔 HOIN ENGINE 진화 제안 알림

승인 대기 중인 제안: 3건

📊 데이터 수집 제안 (2건)
• EVO-20260118-26886
  조건: 외국인 수급 방향 확인 필요
  ✅ 수집 모듈: src/collectors/auto_generated/collect_foreign_investor_flow.py

• EVO-20260118-14701
  조건: 연기금 스탠스 확인 필요
  ✅ 수집 모듈: src/collectors/auto_generated/collect_pension_fund_flow.py

🧠 로직 업데이트 제안 (1건)
• EVO-20260118-LOGIC-001
  조건: MSCI 편입 → 코스피 집중 구조 감지 로직

📌 다음 단계:
1. 대시보드에서 제안 검토
2. 승인 필요 시 → Antigravity에게 구현 요청
3. 거절 시 → 사유 기록

🔗 대시보드: https://hoininsight-commits.github.io/hoininsight/
```

### 2. GitHub Issue

**발송 시점:** Telegram과 동시

**Issue 제목:** `[Human Approval] 3개 진화 제안 구현 필요`

**Issue 내용:**
- 제안별 상세 정보
- 구현 상태 (템플릿 생성 완료 / API 연동 필요)
- 승인 체크리스트
- 대시보드 링크

**Labels:** `evolution`, `human-approval`

---

## 🖥️ 대시보드 사용법

### 1. 제안 검토

대시보드 → **"시스템 진화 제안"** 탭

각 제안 카드에는 다음 정보가 표시됩니다:
- 📊 DATA / 🧠 LOGIC 배지
- 제안 내용 (조건 + 의미)
- 증거 (출처 영상)
- ✅ 수집 모듈 생성 상태 (DATA_ADD인 경우)

### 2. 버튼 옵션

각 제안마다 3개의 버튼이 있습니다:

#### 🟢 승인 (Merge)
- 즉시 승인하여 시스템에 반영
- DATA_COLLECTION_MASTER 자동 업데이트
- 수집 스케줄에 자동 추가

#### 🟠 🤖 Antigravity 요청
- **이 버튼을 클릭하면:**
  1. 추가 요구사항 입력 (선택사항)
  2. GitHub Issue 자동 생성
  3. Antigravity가 다음 세션에서 작업 시작
  
- **Antigravity가 수행할 작업:**
  - 데이터 수집 모듈 완성 (API 연동)
  - 로직 업데이트 (ANOMALY_DETECTION_LOGIC.md)
  - 테스트 및 검증
  - DATA_COLLECTION_MASTER 업데이트
  - 문서화

#### 🔴 거절
- 제안 거절
- 거절 사유 입력 필수
- 거절 목록으로 이동

---

## 🤖 Antigravity 구현 요청 프로세스

### 1. 버튼 클릭 후

**확인 메시지:**
```
🤖 Antigravity 구현 요청

제안 ID: EVO-20260118-26886

다음 작업이 GitHub Issue로 생성됩니다:
1. 데이터 수집 모듈 완성 (API 연동)
2. 로직 업데이트 (필요시)
3. 테스트 및 검증
4. DATA_COLLECTION_MASTER 업데이트

추가 요구사항: [사용자 입력]

계속하시겠습니까?
```

### 2. GitHub Issue 생성

**자동 생성되는 Issue:**
- 제목: `[Antigravity Implementation] EVO-20260118-26886`
- 본문:
  - 제안 상세 정보
  - 구현 체크리스트
  - 사용자 추가 요구사항
  - 관련 파일 경로
  
**Labels:** `antigravity-task`, `implementation`

### 3. Antigravity 작업

사용자가 다음 세션에서 Antigravity에게 알림:

```
"GitHub Issues에 새로운 구현 요청이 있어. 
EVO-20260118-26886 제안을 구현해줘."
```

Antigravity가 자동으로:
1. Issue 내용 확인
2. 수집 모듈 완성 (KRX/DART API 연동)
3. 테스트 실행
4. DATA_COLLECTION_MASTER 업데이트
5. Pull Request 생성
6. Issue 자동 종료

---

## 📋 예시 시나리오

### 시나리오 1: 외국인 수급 데이터 추가

**1. 알림 수신 (Telegram)**
```
📊 데이터 수집 제안
• EVO-20260118-26886
  조건: 외국인 수급 방향 확인 필요
  ✅ 수집 모듈: collect_foreign_investor_flow.py
```

**2. 대시보드 검토**
- 제안 내용 확인
- 수집 모듈 템플릿 확인
- KRX API 연동 필요 확인

**3. Antigravity 요청**
- 🤖 버튼 클릭
- 추가 요구사항 입력: "KOSPI와 KOSDAQ 별도로 수집해줘"

**4. Antigravity 구현**
```python
# collect_foreign_investor_flow.py 완성
- KRX API 연동 완료
- KOSPI/KOSDAQ 분리 로직 추가
- 데이터 검증 로직 추가
- 테스트 완료
```

**5. 자동 배포**
- GitHub Actions에서 자동 실행
- 매일 08:00 데이터 수집
- 이상징후 탐지에 활용

---

## 🔧 설정 확인

### 필수 환경 변수

```bash
# Telegram 알림용
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# GitHub Issue 생성용 (GitHub Actions에서 자동 제공)
GH_TOKEN=${{ github.token }}
```

### 알림 비활성화

Telegram 알림만 비활성화:
```yaml
# .github/workflows/full_pipeline.yml
- name: Notify Human for Approval
  env:
    TELEGRAM_BOT_TOKEN: ""  # 빈 문자열로 설정
```

---

## 📊 모니터링

### 알림 이력 확인

```bash
# 알림 발송 이력
ls data/evolution/notifications/

# 예시 출력:
# EVO-20260118-26886_notified.json
# EVO-20260118-14701_notified.json
```

### 알림 상태 파일

```json
{
  "proposal_id": "EVO-20260118-26886",
  "notified_at": "2026-01-18T05:00:00Z",
  "category": "DATA_ADD",
  "status": "COLLECTOR_GENERATED",
  "channels": ["telegram", "github_issue"]
}
```

---

## 🚨 트러블슈팅

### Telegram 알림이 오지 않을 때

1. 환경 변수 확인
```bash
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID
```

2. GitHub Secrets 확인
- Settings → Secrets and variables → Actions
- `TELEGRAM_BOT_TOKEN` 존재 확인
- `TELEGRAM_CHAT_ID` 존재 확인

### GitHub Issue가 생성되지 않을 때

1. `gh` CLI 설치 확인 (GitHub Actions에서는 자동 설치됨)
2. `GH_TOKEN` 권한 확인
3. Repository 설정에서 Issues 활성화 확인

---

## 🎯 Best Practices

1. **매일 아침 대시보드 확인**
   - Telegram 알림 확인
   - 대시보드에서 제안 검토

2. **즉시 승인 vs Antigravity 요청**
   - 간단한 제안 → 즉시 승인
   - 복잡한 구현 필요 → Antigravity 요청

3. **거절 시 명확한 사유 기록**
   - 나중에 유사한 제안 필터링에 활용

4. **GitHub Issues로 진행 상황 추적**
   - Antigravity 작업 진행도 확인
   - 구현 완료 후 검증

---

## 📝 요약

**자동화된 부분:**
- ✅ 영상 분석 → 제안 생성
- ✅ 수집 모듈 템플릿 생성
- ✅ Telegram + GitHub Issue 알림
- ✅ 대시보드 표시

**사용자 개입 필요:**
- 👤 제안 검토 및 승인/거절 결정
- 👤 Antigravity 구현 요청 (버튼 클릭)

**Antigravity 역할:**
- 🤖 실제 API 연동 구현
- 🤖 로직 업데이트
- 🤖 테스트 및 검증
- 🤖 문서화

**결과:**
- 🚀 완전 자동화된 데이터 수집
- 🚀 지속적으로 진화하는 시스템
- 🚀 사용자는 승인만 하면 됨!
