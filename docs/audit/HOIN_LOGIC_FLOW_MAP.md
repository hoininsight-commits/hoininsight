# HOIN Insight 로직 흐름 맵 (Core Decision Logic)
v1.0 | 2026-04-20 감사 수행

## 1. DETECTOR: 주제 선정 및 필터링 로직

### A. 이상징후 자동 탐지 (Anomaly Detection)
- **SPEED**: 지표의 Z-score가 ±1.5 또는 ±2.0을 돌파할 때 탐지. (`CollectorAgent`에서 사전 계산)
- **CORRELATION**: 지표 간 모순 발생 시 탐지. (`DetectorAgent.detect_correlation_anomalies`)
  - 예: Rally in Fear (주가 상승 + VIX 상승)
  - 예: Price-Position Mismatch (주가 상승 + 헤지펀드 숏 전환)
- **NEWS_MISMATCH**: 뉴스 톤과 지수가 반대로 움직일 때 탐지. (`DetectorAgent._detect_news_mismatch`)

### B. 최종 Top-1 선정 우선순위
`DetectorAgent.select_best` 함수에서 다음 순서로 1개 주제를 최종 낙점함:
1.  **NEWS_MISMATCH**: 뉴스 악재를 압도하는 수급 포착 시 최우선. (강도 9.2+)
2.  **CONSENSUS_SURPRISE**: 예측치 대비 괴리율이 5% 이상인 지표 발표 시.
3.  **CORRELATION_ANOMALY**: 통계적 상관관계 붕괴 발생 시.
4.  **LLM_INSIGHT**: AI가 자율적으로 포착한 복합 서사 중 강도가 높은 것.
5.  **FALLBACK**: Z-score가 가장 큰 단일 지표 이탈 현상.

---

## 2. ANALYST: 심층 분석 및 3계층 문장 관리

### A. 3계층 감옥 규칙 (Sentence Control)
- **[F] FACT**: 데이터로 확인된 수치.
- **[I] INTERPRETATION**: 현상에 대한 해석 (반드시 해석형 어미 "~시사한다" 사용 강제).
- **[S] SPECULATION**: 데이터 없는 추측 (필터링 단계에서 전면 삭제).

### B. 종목 매핑 브리지 (Stock Mapping)
- `sector_map.py` 기반으로 섹터를 추출하되, `AnalystAgent.map_stocks`에서 **데이터 근거가 있는 섹터만 필터링**함.
  - 예: 유가 토픽일 경우에만 에너지 섹터 허용.
  - 예: 나스닥 토픽일 경우 금리/달러 연결 고리가 분석에 있어야 기술주 허용.

---

## 3. WRITER: 경제사냥꾼 7단계 스토리 빌드업

### A. 고정 스토리 템플릿
1.  **Hook (모순)**: 당연한 세상 뒤의 이상함 질문.
2.  **Expectation vs Reality**: 대중의 기대와 차가운 현실의 충돌.
3.  **Mechanism**: 자본이 움직이는 구조적 원인 설명.
4.  **WHY NOW**: 하필 오늘인 이유를 **수치(Z-score 등)**로 증명.
5.  **Implication**: 포지션별(보유자/대기자) 임팩트 분리 해석.
6.  **Mentionables**: 데이터로 검증된 종목/섹터 제시.
7.  **Risk (A/B/C)**: 세 가지 시나리오 대응 전략 제시.

### B. A/B/C 시나리오 로직
- **시나리오 A**: 현재 추세 유지 시 (가장 높은 확률).
- **시나리오 B**: 상황 악화 및 리스크 현실화 시.
- **시나리오 C**: 현재 해석이 틀리거나 판이 뒤집히는 조건.

---

## 4. 주제 탈락(DROP/HOLD) 로직
- **DROP (필터링)**: `DetectorAgent._is_absolute_value_topic`에서 "최고가 돌파" 등 단순히 수치만 도달하고 모순이 없는 주제는 전면 배제.
- **HOLD (우선순위)**: 선정 단계에서 강도가 낮거나(strength < 8.0) 데이터 무결성이 낮은 후보는 큐에 남아 `signal_log`에만 기록되고 발행되지 않음.
