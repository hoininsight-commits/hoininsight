# FRED API 키 발급 및 데이터 수집 가이드

## 📋 Step 1: API 키 발급 (5분)

### 1-1. API Keys 페이지 이동
현재 화면에서 왼쪽 사이드바를 보면:
- **API Keys** 메뉴를 클릭하세요
- 또는 직접 이동: https://fredaccount.stlouisfed.org/apikeys

### 1-2. API 키 생성
1. "Request API Key" 또는 "Create API Key" 버튼 클릭
2. 용도 입력: "HOIN ENGINE Data Collection"
3. 생성 완료!

### 1-3. API 키 복사
- 생성된 키를 복사하세요 (예: `abcd1234efgh5678ijkl9012mnop3456`)
- 이 키는 나중에 다시 볼 수 있으니 걱정 마세요

---

## 📊 Step 2: 각 데이터 시리즈 ID 찾기

FRED에서 데이터를 가져오려면 **Series ID**가 필요합니다.

### 주요 데이터 시리즈 ID 목록

#### 1. 금리 (Interest Rates)
| 데이터 | Series ID | 설명 |
|---|---|---|
| Fed Funds Rate | `FEDFUNDS` | 연준 기준금리 |
| 2Y Treasury | `DGS2` | 2년 국채 금리 |
| 5Y Treasury | `DGS5` | 5년 국채 금리 |
| 10Y Treasury | `DGS10` | 10년 국채 금리 |
| 30Y Treasury | `DGS30` | 30년 국채 금리 |

#### 2. 물가 (Inflation)
| 데이터 | Series ID | 설명 |
|---|---|---|
| CPI | `CPIAUCSL` | 소비자물가지수 |
| Core CPI | `CPILFESL` | 근원 CPI (식품/에너지 제외) |
| PCE | `PCE` | 개인소비지출 |
| Core PCE | `PCEPILFE` | 근원 PCE |
| PPI | `PPIACO` | 생산자물가지수 |

#### 3. 고용 (Employment)
| 데이터 | Series ID | 설명 |
|---|---|---|
| 실업률 | `UNRATE` | Unemployment Rate |
| 비농업 고용 (NFP) | `PAYEMS` | Nonfarm Payrolls |
| 노동참가율 | `CIVPART` | Labor Force Participation |

#### 4. 통화량 (Money Supply)
| 데이터 | Series ID | 설명 |
|---|---|---|
| M1 | `M1SL` | M1 통화량 |
| M2 | `M2SL` | M2 통화량 |

#### 5. 신용/스프레드 (Credit)
| 데이터 | Series ID | 설명 |
|---|---|---|
| HY Spread | `BAMLH0A0HYM2` | High Yield Spread |
| IG Spread | `BAMLC0A4CBBB` | Investment Grade Spread |
| 금융 스트레스 지수 | `STLFSI2` | St. Louis Fed Financial Stress |

#### 6. 기타 거시지표
| 데이터 | Series ID | 설명 |
|---|---|---|
| GDP | `GDP` | 실질 GDP |
| 소비자심리 | `UMCSENT` | University of Michigan Consumer Sentiment |
| VIX | `VIXCLS` | CBOE Volatility Index |

---

## 🔍 Step 3: 데이터 시리즈 ID 직접 찾는 방법

### 방법 1: FRED 검색
1. https://fred.stlouisfed.org/ 메인 페이지
2. 검색창에 데이터 이름 입력 (예: "Fed Funds Rate")
3. 결과 클릭
4. URL에서 Series ID 확인
   - 예: `https://fred.stlouisfed.org/series/FEDFUNDS`
   - Series ID = `FEDFUNDS`

### 방법 2: 데이터 페이지에서 확인
1. 데이터 차트 페이지로 이동
2. 페이지 상단에 "Series ID: XXXXX" 표시됨

---

## 💻 Step 4: Python으로 데이터 가져오기

### 4-1. 라이브러리 설치
```bash
pip install fredapi pandas
```

### 4-2. 기본 사용법
```python
from fredapi import Fred
import pandas as pd

# API 키 설정
fred = Fred(api_key='your_api_key_here')

# 데이터 가져오기
data = fred.get_series('FEDFUNDS')  # Fed Funds Rate
print(data.tail())
```

### 4-3. 날짜 범위 지정
```python
# 최근 1년 데이터
data = fred.get_series('FEDFUNDS', 
                       observation_start='2025-01-01',
                       observation_end='2026-01-18')
```

### 4-4. 여러 데이터 한번에 가져오기
```python
series_ids = {
    'FEDFUNDS': 'Fed Funds Rate',
    'DGS10': '10Y Treasury',
    'CPIAUCSL': 'CPI',
    'UNRATE': 'Unemployment Rate'
}

data_dict = {}
for series_id, name in series_ids.items():
    data_dict[name] = fred.get_series(series_id)
    
# DataFrame으로 변환
df = pd.DataFrame(data_dict)
print(df.tail())
```

---

## 🚀 Step 5: HOIN ENGINE용 수집기 구현

### 5-1. Fed Funds Rate 수집기
```python
# src/collectors/fred_fedfunds.py
from fredapi import Fred
from pathlib import Path
from datetime import datetime
import pandas as pd
import os

def collect_fedfunds():
    """Collect Fed Funds Rate from FRED"""
    
    # API 키 가져오기
    api_key = os.environ.get('FRED_API_KEY')
    if not api_key:
        print("[FRED] API key not found in environment")
        return
    
    # FRED 연결
    fred = Fred(api_key=api_key)
    
    # 데이터 수집
    try:
        data = fred.get_series('FEDFUNDS')
        
        # 저장 경로
        base_dir = Path(__file__).parent.parent.parent
        output_dir = base_dir / "data" / "raw" / "rates" / "fed_funds"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # CSV 저장
        df = pd.DataFrame({
            'date': data.index,
            'value': data.values
        })
        
        output_file = output_dir / f"fedfunds_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(output_file, index=False)
        
        print(f"[FRED] Fed Funds Rate saved: {output_file}")
        print(f"[FRED] Latest value: {data.iloc[-1]:.2f}%")
        
    except Exception as e:
        print(f"[FRED] Error: {e}")

if __name__ == "__main__":
    collect_fedfunds()
```

### 5-2. 통합 FRED 수집기
```python
# src/collectors/fred_collector.py
from fredapi import Fred
from pathlib import Path
from datetime import datetime
import pandas as pd
import os

class FREDCollector:
    """FRED 데이터 통합 수집기"""
    
    SERIES_MAP = {
        # 금리
        'FEDFUNDS': {'category': 'rates', 'name': 'fed_funds_rate'},
        'DGS2': {'category': 'rates', 'name': 'us_2y_yield'},
        'DGS10': {'category': 'rates', 'name': 'us_10y_yield'},
        'DGS30': {'category': 'rates', 'name': 'us_30y_yield'},
        
        # 물가
        'CPIAUCSL': {'category': 'inflation', 'name': 'cpi'},
        'CPILFESL': {'category': 'inflation', 'name': 'core_cpi'},
        'PCE': {'category': 'inflation', 'name': 'pce'},
        'PCEPILFE': {'category': 'inflation', 'name': 'core_pce'},
        
        # 고용
        'UNRATE': {'category': 'employment', 'name': 'unemployment_rate'},
        'PAYEMS': {'category': 'employment', 'name': 'nonfarm_payrolls'},
        
        # 통화량
        'M1SL': {'category': 'money_supply', 'name': 'm1'},
        'M2SL': {'category': 'money_supply', 'name': 'm2'},
        
        # 신용
        'BAMLH0A0HYM2': {'category': 'credit', 'name': 'hy_spread'},
        'STLFSI2': {'category': 'credit', 'name': 'financial_stress'},
    }
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('FRED_API_KEY')
        if not self.api_key:
            raise ValueError("FRED API key not found")
        self.fred = Fred(api_key=self.api_key)
        self.base_dir = Path(__file__).parent.parent.parent
    
    def collect_series(self, series_id):
        """단일 시리즈 수집"""
        try:
            data = self.fred.get_series(series_id)
            
            # 메타데이터
            info = self.SERIES_MAP.get(series_id, {})
            category = info.get('category', 'other')
            name = info.get('name', series_id.lower())
            
            # 저장 경로
            output_dir = self.base_dir / "data" / "raw" / "fred" / category
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # CSV 저장
            df = pd.DataFrame({
                'date': data.index,
                'value': data.values
            })
            
            output_file = output_dir / f"{name}.csv"
            df.to_csv(output_file, index=False)
            
            print(f"[FRED] ✓ {series_id} ({name}): {len(data)} records")
            return True
            
        except Exception as e:
            print(f"[FRED] ✗ {series_id}: {e}")
            return False
    
    def collect_all(self):
        """모든 시리즈 수집"""
        print(f"[FRED] Collecting {len(self.SERIES_MAP)} series...")
        
        success_count = 0
        for series_id in self.SERIES_MAP.keys():
            if self.collect_series(series_id):
                success_count += 1
        
        print(f"[FRED] Complete: {success_count}/{len(self.SERIES_MAP)} series")

def main():
    collector = FREDCollector()
    collector.collect_all()

if __name__ == "__main__":
    main()
```

---

## ✅ Step 6: 환경 변수 설정

### 6-1. .env 파일 생성
```bash
# HoinInsight/.env
FRED_API_KEY=your_api_key_here
```

### 6-2. GitHub Secrets 설정
```bash
# GitHub Repository → Settings → Secrets → Actions
# New repository secret:
# Name: FRED_API_KEY
# Value: your_api_key_here
```

---

## 🎯 빠른 시작 가이드

### 1단계: API 키 발급
1. 왼쪽 사이드바 "API Keys" 클릭
2. "Request API Key" 클릭
3. 키 복사

### 2단계: 테스트
```bash
cd HoinInsight
export FRED_API_KEY="your_key"
python3 -c "from fredapi import Fred; f=Fred('your_key'); print(f.get_series('FEDFUNDS').tail())"
```

### 3단계: 수집기 실행
```bash
python3 src/collectors/fred_collector.py
```

---

## 📚 참고 자료

- FRED API 문서: https://fred.stlouisfed.org/docs/api/fred/
- Python fredapi: https://github.com/mortada/fredapi
- Series 검색: https://fred.stlouisfed.org/
- API 사용 제한: 120 requests/minute (매우 넉넉함)

---

## ⚡ 자주 사용하는 Series ID 치트시트

```python
# 복사해서 사용하세요!
FRED_SERIES = {
    # 금리
    'FEDFUNDS',    # Fed Funds Rate
    'DGS10',       # 10Y Treasury
    
    # 물가
    'CPIAUCSL',    # CPI
    'PCEPILFE',    # Core PCE
    
    # 고용
    'UNRATE',      # Unemployment
    'PAYEMS',      # NFP
    
    # 통화
    'M2SL',        # M2
    
    # 신용
    'BAMLH0A0HYM2', # HY Spread
}
```
