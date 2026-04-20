# ANALYST 설계 원칙
v1.0 | 2026-04-20

## 역할
DETECTOR가 선정한 주제를 바탕으로 심층적인 구조적 원인(Mechanism)을 분석하고, 이 변화가 실질적으로 어떤 섹터와 종목에 임팩트를 주는지 매핑한다.

## 입력 / 출력
- **입력**: `today_signal.json`, `data/raw/` 전체 (특히 FRED, DART, COT 데이터)
- **출력**: `today_analysis.json` (논리 구조), `today_stocks.json` (연결 종목)

## 핵심 로직
1. **WHY NOW Deep Dive**: 과거 90일 히스토리를 대조하여 현재 시그널의 역사적/구조적 희소성 검증
2. **Sector Mapping**: `sector_map.py`를 활용하여 토픽과 연관된 1차/2차 수혜/피해 섹터 추출
3. **Stock Discovery**: 각 섹터별 지배적 사업자(Bottleneck) 및 최근 공시(DART) 기반 유효 종목 필터링
4. **Logic Synthesis**: [현상] → [원인] → [결과] → [대응]으로 이어지는 사냥꾼의 논리 체계 구성 (LLM 활용)

## 수정 시 주의사항
- 종목 추천이 아닌 "데이터 브리지"에 집중할 것
- 근거 없는 종목 나열 금지 (반드시 관련 섹터나 공시 근거가 있어야 함)

## 알려진 이슈
- 국내외 종목 데이터베이스(Sector Map)의 상시 업데이트 필요
