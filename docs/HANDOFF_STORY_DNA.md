# HOIN Insight v10.2 [Autonomous Discovery] Handover

## 1. 핵심 진화 사항 (The Great Leap)
- **Zero-Shot Autonomous Discovery**: 섹터나 키워드 가이드 없이도 실시간 지표와 뉴스에서 시장의 '새로운 축(Frontier Axis)'을 스스로 탐지합니다. (`AxisDetector`)
- **Deterministic Veracity Guard**: AI가 수치를 오독하거나 상투적인 오프닝("이상한 점...")을 쓰지 못하도록 결정론적 검증 로직을 `ScriptQualityGate`에 이식했습니다.
- **Thematic Purity**: 훅(Hook)과 핵심 팩트(WHY NOW)가 100% 동일한 테마를 공유하도록 강제하여 콘텐츠의 논리적 완결성을 확보했습니다.

## 2. 엔진 가동 가이드
- **실행**: `python3 src/agents/detector.py` -> `python3 src/agents/writer.py`
- **배포**: `python3 src/ui/run_publish_ui_decision_assets.py` 실행 시 대시보드 데이터 전송
- **검열**: `src/engine/script_quality_gate.py`에서 금지어 및 수치 무결성을 실시간 체킹합니다.

## 3. 사냥꾼의 DNA (Style Guide)
- **반말 화법**: 시청자에게 직접 던지는 날카로운 반말투 유지.
- **데이터 증거**: 모든 문장은 `[F]`(팩트)와 `[I]`(해석) 태그가 붙어야 하며, 팩트는 제공된 `core_facts`에서만 가져와야 합니다.
- **클리셰 금지**: "요즘 시장을 보면..." 같은 지루한 인사는 1점 처리되어 폐기됩니다. 무조건 그날의 핵심 팩트로 시장을 여십시오.

## 4. 제거된 유산들 (Purged Legacy)
- `src/utils/tickers/` (하드코딩 티커 로직)
- `src/utils/hoin/` (구형 오케스트레이터)
- `docs/*.md` (100여 개의 구식 SPEC 문서)

---
*본 문서는 2026-04-24 대청소 이후 생성된 최종 SSOT(Single Source of Truth)입니다.*
