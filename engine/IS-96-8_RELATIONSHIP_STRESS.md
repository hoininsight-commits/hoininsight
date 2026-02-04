# Relationship Stress Signal Layer (IS-96-8)

## 1. 개요 (Overview)
Relationship Stress Layer는 시장 주도 기업들 간의 "파트너십 균열" 또는 "루프 의존성 스트레스"를 탐지합니다. (예: NVIDIA ↔ OpenAI 파트너십의 긴장 상태). 이는 단순한 소문이 아닌, 결정론적 지표들(계약 재산정, 성명서 불일치 등)의 조합을 통해 포착됩니다.

## 2. 탐지 대상 (Targets)
- **Strategic Partner**: 공동 기술 개발 또는 독점 마케팅 연합.
- **Capital Loop**: 순환 출자 또는 한 쪽의 자본 주입 의존도가 높은 관계.
- **Supplier Dependency**: 공급망 상의 독점적 지위 점유 관계.
- **Distribution Dependency**: 판매 채널의 70% 이상을 특정 파트너가 점유한 관계.

## 3. 결정론적 스코어링 (Deterministic Scoring)
Stress Score는 다음 가중 지표의 합으로 구성됩니다 (0.0 - 1.0):

| 지표 (Indicator) | 가중치 (Weight) | 설명 |
| :--- | :--- | :--- |
| **Deal Reprice** | 0.35 | 공급 단가 재산정 또는 계약 조건 변경 신호 |
| **Statement Divergence** | 0.25 | 미래 전략에 대한 양사 공식 입장 차이 발생 |
| **Capital Link Change** | 0.20 | 지분 매각, 투자 계획 축소, EXIT 신호 |
| **Supply Dependency** | 0.20 | 대체 공급자 탐색 또는 공급 중단 경고 |

## 4. Break Risk 등급 (Break Risk Levels)
- **HIGH**:
  - `stress_score >= 0.75`
  - 독립된 소스 개수 `n >= 2`
  - 평균 소스 신뢰도 `avg_reliability >= 0.7`
- **MED**:
  - `stress_score >= 0.55`
- **LOW**:
  - 그 외

## 5. 해석 어셈블리 출력 (Interpretation Assembly)
Break Risk가 **HIGH**인 경우 `interpretation_units.json`에 `RELATIONSHIP_BREAK_RISK` 테마가 발행됩니다. **MED**이면서 신뢰도가 낮은 경우 `Hypothesis Jump (HOLD)` 프레임을 적용합니다.
