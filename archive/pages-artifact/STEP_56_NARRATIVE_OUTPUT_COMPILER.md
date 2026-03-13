# STEP 56 — NARRATIVE OUTPUT COMPILER (Constitution)

## 1. 목적 (Goal)
모든 분석 단계(Step 0-55)를 집대성하여, 대시보드와 사용자에게 전달될 최종 형태의 "Economic Hunter Card"를 생성한다.

## 2. 컴파일 규칙 (Compilation Rules)

### 2-1. YAML First
- **Rule**: 모든 출력은 기계 가독성이 높은 YAML 포맷으로 우선 생성한다.
- **Rationale**: 이후 LLM Narrator나 UI 렌더러가 데이터를 손쉽게 가공할 수 있게 하기 위함.

### 2-2. Zero Jargon (Human-Centric)
- **Rule**: 최종 출력문의 'Description'은 전문 용어를 최소화하고 구조적 본질을 꿰뚫는 직관적인 언어로 기술한다.

### 2-3. Trace Inclusion
- **Rule**: 분석의 신뢰도를 위해 `reasoning_trace`와 `evidence_anchors`를 반드시 포함해야 한다.

## 3. 최종 출력 규격 (Final Card Schema)
```yaml
economic_hunter_card:
  version: "1.0"
  topic_id: "EH-2026-001"
  title: "[경보] 2nm 파운드리 병목과 공급망 재편"
  summary: "TSMC의 선단공정 수율 부진이 칩 설계사들의 출시 지연으로 전이되는 핵심 국면 포착."
  
  # Step 52
  targets:
    - ticker: "ASML"
      role: "ENABLER"
    - ticker: "TSM"
      role: "OWNER"
      
  # Step 53
  trace:
    - "ANOMALY: TSMC 2nm yield rumors"
    - "STRUCTURAL: Foundry bottleneck shift"
    - "WHY_NOW: iPhone AP production window"
    
  # Step 54
  anchors:
    - "STOOQ: TSM Relative Strength drop"
    - "DART: Supplier equipment delay notice"
    
  # Step 55
  meta:
    confidence: 88
    status: "READY"
    narrative_format: "ECONOMIC_HUNTER_VIDEO"
```

## 4. 배포 프로세스 (Deployment)
1. **Serialization**: YAML 파일 생성 (`data/reports/YYYY/MM/DD/eh_card.yaml`).
2. **Dashboard Injection**: 대시보드 매니페스트에 경로 등록.
3. **Notification**: 텔레그램/슬랙 등 알림 채널 전송.
