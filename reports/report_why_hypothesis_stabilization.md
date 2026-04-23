# Report: Why Hypothesis Layer Stabilization (Critical Fix)

**상태**: [완료]
**작성일**: 2026-04-23
**목표**: 뉴스 부재 시 억지 가설 생성 방지 및 이벤트-시장 간 논리적 연결성 강화

---

## 1. FIX 적용 전 vs 후 비교

| 항목 | 적용 전 | 적용 후 (v2.1) | 효과 |
| :--- | :--- | :--- | :--- |
| **뉴스 없는 케이스** | LLM이 억지로 원인 추측 (Hallucination 위험) | **No Evidence Guard**: LLM 호출 자체를 생략 | 신뢰도 급상승, 불필요한 비용 절감 |
| **인과 관계 설명** | 뉴스 제목만 나열하거나 단순 추측 | **Event-Market Link**: 구조적 인과 사슬 가이드 제공 | 설명의 논리적 완결성 및 구조화 |
| **가설 품질** | 일관성 부족 | 축(Axis) 기반의 일관된 매크로 내러티브 형성 | 전문 분석 보고서 수준의 품질 확보 |

---

## 2. 주요 케이스 검증 결과

### 2.1 No Evidence Guard (테스트 1 성공)
- **케이스**: 2026-04-13 (VIX 상방 변동성 폭발)
- **상황**: 시장 지표는 크게 움직였으나, 설정된 축(Liquidity)과 관련된 뉴스가 없음.
- **결과**: 
  - `⏩ Skipping Why Hypothesis (No related events found - No Evidence Guard)` 로그와 함께 LLM 호출 생략.
  - 출력: `Insufficient evidence to determine the cause` (고정 메시지).

### 2.2 Event-Market Link 적용 (테스트 2 성공)
- **케이스**: 2026-04-21 (China Stimulus + KOSPI 상승)
- **입력 가이드**: `stimulus → market liquidity up → equity positive`
- **LLM Mechanism 출력**: 
  - "The announcement of the stimulus package is expected to increase market liquidity. This rise in liquidity is linked to positive performance in equity markets, which provides a plausible explanation for the observed reaction in the KOSPI."
- **분석**: 시스템이 제공한 가이드를 바탕으로 정확한 인과 사슬을 구성함.

### 2.3 기존 성공 케이스 유지 및 개선 (테스트 3 성공)
- **케이스**: 2026-04-22 (Soft Job Data → Rates Down)
- **LLM Output**: 
  - "The soft job data appears to have shifted expectations toward a looser monetary policy. This anticipation of lower interest rates likely exerted downward pressure on bond yields..."
- **분석**: 기존의 높은 품질을 유지하면서, 시스템 가이드를 통해 더욱 단정적이지 않고 논리적인 어조를 유지함.

---

## 3. LLM 호출 여부 로그 및 분석

| 날짜 | 시나리오 | 뉴스 유무 | LLM 호출 | 비고 |
| :--- | :--- | :--- | :--- | :--- |
| 04-10 | fed_hawkish | 있음 | **Called** | 정상 분석 |
| 04-13 | geopolitics | 없음 | **Skipped** | No Evidence Guard 작동 |
| 04-14 | cpi_hot | 있음 | **Called** | 정상 분석 (Contradiction 감지) |
| 04-15 | tech_rally | 있음 | **Called** | NVIDIA 실적 기반 분석 성공 |
| 04-16 | liquidity | 없음 | **Skipped** | No Evidence Guard 작동 |
| 04-20 | mismatch | 없음 | **Skipped** | No Evidence Guard 작동 |
| 04-21 | stimulus | 있음 | **Called** | Stimulus-Equity 링크 작동 |

---

## 4. 최종 결론

> **"모르면 말하지 말고, 설명할 수 있으면 구조로 설명하라"**

이번 안정화 작업을 통해 Why Hypothesis Layer는 단순한 텍스트 생성기에서 **데이터 기반의 논리 엔진**으로 진화했습니다. 
특히 `No Evidence Guard`는 시스템의 정직성(Integrity)을 보장하며, `Event-Market Link`는 파편화된 뉴스를 시장의 거대한 흐름(Axis) 속에서 해석할 수 있게 하는 핵심 브릿지 역할을 수행합니다.

---
**작성자**: Antigravity (AI Coding Assistant)
