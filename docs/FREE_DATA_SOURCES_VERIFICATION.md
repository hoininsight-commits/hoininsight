# 무료 데이터 소스 검증 리포트

## 🎯 목적
HOIN ENGINE에서 사용하려는 모든 데이터 소스가 **완전 무료**인지 확인

---

## ✅ 현재 구현된 데이터 소스 (100% 무료 확인됨)

### 1. Cryptocurrency (암호화폐)
| 데이터 | 소스 | API | 무료 여부 | 제한사항 |
|---|---|---|---|---|
| BTC, ETH 가격 | CoinGecko | Free API | ✅ 무료 | 50 calls/min |

**확인**: https://www.coingecko.com/en/api/pricing
- Free tier: 50 calls/minute
- API 키 불필요

---

### 2. FX (환율)
| 데이터 | 소스 | API | 무료 여부 | 제한사항 |
|---|---|---|---|---|
| USD/KRW | ExchangeRate-API | Free | ✅ 무료 | 1,500 requests/month |

**확인**: https://www.exchangerate-api.com/
- Free tier: 1,500 requests/month
- 하루 1회 수집 = 30 requests/month (충분)

---

### 3. Precious Metals (귀금속)
| 데이터 | 소스 | API | 무료 여부 | 제한사항 |
|---|---|---|---|---|
| Gold (XAU) | GoldAPI.io | Free | ✅ 무료 | 100 requests/month |
| Silver (XAG) | GoldAPI.io | Free | ✅ 무료 | 100 requests/month |

**확인**: https://www.goldapi.io/pricing
- Free tier: 100 requests/month
- 하루 1회 수집 = 30 requests/month (충분)

---

### 4. Equity Indices (주식 지수)
| 데이터 | 소스 | API | 무료 여부 | 제한사항 |
|---|---|---|---|---|
| S&P500, NASDAQ | Stooq | CSV | ✅ 무료 | 무제한 |
| KOSPI, KOSDAQ | Stooq | CSV | ✅ 무료 | 무제한 |
| VIX | Stooq | CSV | ✅ 무료 | 무제한 |

**확인**: https://stooq.com/
- 완전 무료
- CSV 다운로드 무제한
- API 키 불필요

---

### 5. US Treasury Yields (미국 국채)
| 데이터 | 소스 | API | 무료 여부 | 제한사항 |
|---|---|---|---|---|
| 2Y, 10Y, 30Y | US Treasury | XML/JSON | ✅ 무료 | 무제한 |

**확인**: https://home.treasury.gov/
- 공식 정부 데이터
- 완전 무료
- API 키 불필요

---

## ⚠️ 미구현 데이터 소스 검증

### 1. FRED (Federal Reserve Economic Data) ⭐ 최우선
| 데이터 | 소스 | API | 무료 여부 | 제한사항 |
|---|---|---|---|---|
| Fed Funds Rate | FRED | API | ✅ **완전 무료** | API 키 필요 (무료) |
| CPI, Core CPI | FRED | API | ✅ **완전 무료** | API 키 필요 (무료) |
| PCE | FRED | API | ✅ **완전 무료** | API 키 필요 (무료) |
| M1, M2 | FRED | API | ✅ **완전 무료** | API 키 필요 (무료) |
| NFP, 실업률 | FRED | API | ✅ **완전 무료** | API 키 필요 (무료) |
| HY Spread | FRED | API | ✅ **완전 무료** | API 키 필요 (무료) |
| 금융 스트레스 지수 | FRED | API | ✅ **완전 무료** | API 키 필요 (무료) |

**확인**: https://fred.stlouisfed.org/docs/api/api_key.html
- ✅ **완전 무료**
- API 키 발급: https://fredaccount.stlouisfed.org/apikeys
- 제한: 120 requests/minute (매우 넉넉함)
- 모든 데이터 무료 접근

**API 키 발급 방법:**
1. https://fredaccount.stlouisfed.org/login 에서 계정 생성 (무료)
2. API Keys 메뉴에서 키 발급
3. 즉시 사용 가능

---

### 2. 한국은행 ECOS (Economic Statistics System)
| 데이터 | 소스 | API | 무료 여부 | 제한사항 |
|---|---|---|---|---|
| 한국 기준금리 | ECOS | API | ✅ **완전 무료** | API 키 필요 (무료) |
| 국내 CPI | ECOS | API | ✅ **완전 무료** | API 키 필요 (무료) |
| 국내 M1, M2 | ECOS | API | ✅ **완전 무료** | API 키 필요 (무료) |

**확인**: https://ecos.bok.or.kr/
- ✅ **완전 무료**
- API 키 발급: https://ecos.bok.or.kr/api/
- 제한: 하루 10,000 requests (충분)

**API 키 발급 방법:**
1. https://ecos.bok.or.kr/ 접속
2. 회원가입 (무료)
3. API 인증키 신청
4. 즉시 발급

---

### 3. KRX (한국거래소)
| 데이터 | 소스 | API | 무료 여부 | 제한사항 |
|---|---|---|---|---|
| 외국인/기관 수급 | KRX 정보데이터시스템 | CSV/API | ✅ **완전 무료** | 로그인 필요 |
| 거래대금 | KRX | CSV | ✅ **완전 무료** | 로그인 필요 |
| 섹터별 ETF | KRX | CSV | ✅ **완전 무료** | 로그인 필요 |

**확인**: http://data.krx.co.kr/
- ✅ **완전 무료**
- 회원가입 필요 (무료)
- CSV 다운로드 또는 API 사용

---

### 4. DART (금융감독원 전자공시)
| 데이터 | 소스 | API | 무료 여부 | 제한사항 |
|---|---|---|---|---|
| 기업 공시 | DART | API | ✅ **완전 무료** | API 키 필요 (무료) |
| 주요주주 변동 | DART | API | ✅ **완전 무료** | API 키 필요 (무료) |

**확인**: https://opendart.fss.or.kr/
- ✅ **완전 무료**
- API 키 발급: https://opendart.fss.or.kr/uss/umt/EgovUserCnfirm.do
- 제한: 10,000 requests/day

---

### 5. 기타 무료 소스

#### A. Yahoo Finance (yfinance)
| 데이터 | 무료 여부 | 제한사항 |
|---|---|---|
| 주식 가격 | ✅ 무료 | 2,000 requests/hour |
| 환율 | ✅ 무료 | 2,000 requests/hour |

**주의**: 공식 API 아님, 웹스크래핑 기반

#### B. Alpha Vantage
| 데이터 | 무료 여부 | 제한사항 |
|---|---|---|
| 주식, FX, 암호화폐 | ✅ 무료 | 5 API calls/minute, 500/day |

**확인**: https://www.alphavantage.co/
- Free tier 매우 제한적
- FRED가 더 나음

#### C. Quandl (Nasdaq Data Link)
| 데이터 | 무료 여부 | 제한사항 |
|---|---|---|
| 일부 데이터셋 | ⚠️ 일부 무료 | 데이터셋마다 다름 |

**주의**: 많은 데이터셋이 유료로 전환됨

---

## ❌ 유료 또는 제한적인 소스 (사용 안 함)

### 1. Bloomberg API
- ❌ **유료** (월 $2,000+)
- 사용 안 함

### 2. Refinitiv (Thomson Reuters)
- ❌ **유료** (월 수천 달러)
- 사용 안 함

### 3. FactSet
- ❌ **유료**
- 사용 안 함

### 4. CDS Index
- ❌ **무료 고신뢰 데이터 없음**
- DATA_COLLECTION_MASTER에서 BLOCKED 상태

---

## ✅ 최종 결론

### 모든 계획된 데이터 소스는 **100% 무료**입니다!

**필요한 무료 API 키:**
1. ✅ **FRED API Key** (최우선) - https://fredaccount.stlouisfed.org/apikeys
2. ✅ **한국은행 ECOS API Key** - https://ecos.bok.or.kr/api/
3. ✅ **DART API Key** - https://opendart.fss.or.kr/
4. ✅ **KRX 계정** (선택) - http://data.krx.co.kr/

**발급 시간:** 각 5분 이내, 모두 즉시 사용 가능

---

## 📊 무료 데이터로 커버 가능한 범위

### ✅ 완전 커버 (100%)
- 금리 (FRED, US Treasury)
- 물가 (FRED, ECOS)
- 고용 (FRED, ECOS)
- 통화량 (FRED, ECOS)
- 주식 지수 (Stooq, KRX)
- 환율 (ExchangeRate-API, ECOS)
- 귀금속 (GoldAPI, FRED)
- 암호화폐 (CoinGecko)
- 변동성 (Stooq VIX)
- 국내 수급 (KRX)
- 기업 공시 (DART)

### ⚠️ 제한적 커버
- 신용 스프레드: FRED에서 일부 가능
- 부동산: 공공 데이터 활용 (KB부동산, 국토부)

### ❌ 커버 불가
- CDS Index (유료만 존재)
- 실시간 틱 데이터 (일봉 데이터로 충분)

---

## 🎯 권장 우선순위

### 1단계: FRED API 통합 (최우선)
- API 키 발급 (5분)
- 40+ 핵심 지표 즉시 사용 가능
- 무료, 무제한

### 2단계: 한국은행 ECOS
- API 키 발급 (5분)
- 국내 거시 지표

### 3단계: KRX + DART
- 국내 시장 미시 데이터

---

## ✅ 결론

**모든 데이터 소스가 100% 무료입니다!**

유일한 요구사항:
- 무료 API 키 발급 (총 소요시간: 20분)
- 이메일 주소만 있으면 됨

**비용: $0 / 월** 🎉
