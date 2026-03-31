# [PHASE-28] Structural Meta-Volatility Engine v1.0

## 1. 목적
시장의 “구조적 변동성 상태”를 3가지 축(압축, 팽창, 취약성)으로 정의하여 운영자에게 즉각적인 인사이트를 제공한다.

## 2. 입력 및 출력
### 입력 (Read-only)
- `regime_state.json`
- `investment_os_state.json`
- `timing_state.json`
- `probability_compression_state.json`
- `conflict_density_pack.json`
- `video_candidate_pool.json`

### 출력
- `meta_volatility_state.json`: 구조화된 상태 데이터
- `meta_volatility_brief.md`: 운영자용 브리프

## 3. 룰 엔진 (Classification Rules)
### Mode (상태 모드)
- **COMPRESSION**: 에너지가 응축되는 단계 (Probability Compression Pressure HIGH + Timing Gear 불일치 등)
- **EXPANSION**: 에너지가 방출되는 단계 (Conflict HIGH + Gear 4 이상 + Video Candidates 다수 등)
- **MIXED**: 판정 불가 또는 상반된 신호 혼재

### Fragility (취약성)
- **HIGH**: TIGHTENING 정권 + 높은 Gear + 낮은 Stability 등 불안정 요소 결합 시
- **MEDIUM**: 일부 지표 불안정
- **LOW**: 완화적 정권 + 높은 Stability + 낮은 Gear

### Shock Window (충격 창)
- **NONE**: 모든 지표 안정
- **WATCH**: 압력 상승 또는 Fragility MEDIUM
- **ELEVATED**: Fragility HIGH + (Gear 4 이상 또는 Conflict HIGH)

## 4. UI 구성 (🌪️ Meta-Volatility)
- **Badges**: Mode, Fragility, Shock Window 상태 표시
- **One-liner**: 현재 상태 요약
- **Why-now**: 3대 근거 (Timing, Compression, Regime 기반)
- **Invalidators**: 무효화 조건

## 5. Remote Endpoint
- `https://hoininsight-commits.github.io/hoininsight/data/ops/meta_volatility_state.json`
- `https://hoininsight-commits.github.io/hoininsight/data/ops/meta_volatility_brief.md`
