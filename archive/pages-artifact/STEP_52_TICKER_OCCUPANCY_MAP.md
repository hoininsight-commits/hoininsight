# STEP 52 — TICKER OCCUPANCY MAP (Constitution)

## 1. 목적 (Goal)
Step 51(Reality Validation)에서 검증된 '병목 현상(Bottleneck)'을 소유하거나, 그로 인해 가장 직접적으로 현금 흐름이 발생하는 핵심 수혜/피해 대상(Ticker)을 연결한다.

## 2. 선정 규칙 (Selection Rules)

### 2-1. Ticker 수량 제한
- **Rule**: 병목 1개당 최소 1개, 최대 3개의 Ticker로 압축한다.
- **Rationale**: 노이즈 제거 및 선명한 타겟 지정을 위해 3개를 초과하지 않는다.

### 2-2. 매출 비중 50% Rule (Revenue Focus)
- **Rule**: 선정된 Ticker는 해당 병목과 관련된 제품/서비스의 매출 비중이 전체의 **50% 이상**이어야 한다.
- **Exception**: 삼성전자, SK하이닉스 등 거대 기업이더라도 해당 섹터의 시장 점유율(Market Share) 1위인 경우, 비중이 50% 미만이라도 포함할 수 있다.

### 2-3. 제조사 우선 원칙 (Manufacturer-First)
- **Rule**: 유통사나 단순 파트너사보다는, 병목 기술을 직접 소유하거나 제조하는 **원천 기업**을 우선 선정한다.
- **Priority List**: 원천 기술 보유사 > 핵심 장비/소재 제조사 > 수직 계열화된 리더.

## 3. 로직 프로세스 (Logic Flow)
1. **Bottleneck Mapping**: Step 51의 병목 키워드와 `entity_mapping_layer`의 엔티티 매칭.
2. **Revenue Validation**: 공시 및 리포트 기반 매출 비중 필터링.
3. **Manufacturer Check**: 벨류체인 상의 위치(Layer) 확인.
4. **Final Selection**: 상위 1-3개 Ticker 리스트 확정.

## 4. 데이터 규격 (Schema)
```yaml
ticker_occupancy:
  - ticker: "TSM"
    name: "TSMC"
    market: "NYSE"
    logic_role: "OWNER"
    revenue_focus: 1.0 # 100%
    rationale: "글로벌 파운드리 병목의 핵심 열쇠를 쥔 기업."
  - ticker: "ASML"
    name: "ASML"
    market: "NASDAQ"
    logic_role: "ENABLER"
    revenue_focus: 0.95
    rationale: "EUV 장비 독점을 통한 선단 공정 병목 제어."
```
