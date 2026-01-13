# 📊 DATA_COLLECTION_MASTER v1.3

> 기준: 중복 제거 + 파생 유지 + 누적 관리  
> 목적: 데이터 수집 → 이상징후 감지 → 주제 선정(선점)

| 카테고리 | 수집 데이터 | 수집처 | 방식 | 무료 여부 | 상태 | WHY | 최적 데이터 수집 시간단위 | 기존 데이터 기반 파생 데이터 여부 |
|---|---|---|---|---|---|---|---|---|
| 금리·유동성·통화 | 미국 기준금리 (Fed Funds Rate) | FRED | API | Free | READY | 글로벌 모든 자산 가격의 기준 축 | 이벤트/1일 | 수집데이터 |
| 금리·유동성·통화 | 한국 기준금리 | 한국은행 ECOS | API/CSV | Free | READY | 국내 자산·부동산·환율 압력의 직접 원인 | 이벤트/1일 | 수집데이터 |
| 금리·유동성·통화 | ECB 기준금리 | ECB | API/RSS | Free | READY | 유럽 금융·글로벌 자금 흐름 영향 | 이벤트/1일 | 수집데이터 |
| 금리·유동성·통화 | 미국 국채금리 2Y | FRED | API | Free | READY | 단기 경기·금리 기대 반영 | 1일 | 수집데이터 |
| 금리·유동성·통화 | 미국 국채금리 5Y | FRED | API | Free | READY | 중기 성장 기대 | 1일 | 수집데이터 |
| 금리·유동성·통화 | 미국 국채금리 10Y | FRED | API | Free | READY | 장기 성장·물가 기대 | 1일 | 수집데이터 |
| 금리·유동성·통화 | 미국 국채금리 30Y | FRED | API | Free | READY | 장기 신뢰·재정 부담 | 1일 | 수집데이터 |
| 금리·유동성·통화 | 금리 스프레드(10Y-2Y) | FRED | 파생 | Free | READY | 경기 전환점 조기 탐지 | 1일 | 파생데이터 |
| 금리·유동성·통화 | SOFR | FRED | API | Free | READY | 단기자금 경색 | 1일 | 수집데이터 |
| 금리·유동성·통화 | LIBOR | FRED | API | Free | READY | 글로벌 단기금리 | 1일 | 수집데이터 |
| 인플레이션·실물 | CPI | FRED/ECOS | API | Free | READY | 인플레이션 판단 | 1개월 | 수집데이터 |
| 인플레이션·실물 | Core CPI | FRED/ECOS | API | Free | READY | 기조 인플레 | 1개월 | 수집데이터 |
| 인플레이션·실물 | PPI | FRED/ECOS | API | Free | READY | 비용 압력 | 1개월 | 수집데이터 |
| 인플레이션·실물 | PCE | FRED | API | Free | READY | 연준 선호 물가지표 | 1개월 | 수집데이터 |
| 주식시장 | S&P500 | Stooq | API/CSV | Free | READY | 글로벌 위험자산 기준 | 1일 | 수집데이터 |
| 주식시장 | NASDAQ | Stooq | API/CSV | Free | READY | 성장주 심리 | 1일 | 수집데이터 |
| 주식시장 | KOSPI | KRX | CSV | Free | READY | 국내 경기 종합 | 1일 | 수집데이터 |
| 파생·변동성 | VIX | FRED | API | Free | READY | 시장 공포 | 1일 | 수집데이터 |
| 신용·스트레스 | 회사채 스프레드 | FRED | API | Free | READY | 신용 위험 | 1일 | 수집데이터 |
| 원자재·에너지 | 금 현물 | FRED/LBMA | API | Free | READY | 위험회피·통화불신 | 1일 | 수집데이터 |
| 암호자산 | BTC 가격 | CoinGecko | API | Free | READY | 위험자산 선행 | 1일 | 수집데이터 |
| 부동산 | 주택가격지수 | 한국부동산원 | CSV | Free | READY | 실물 자산 | 1개월 | 수집데이터 |
| 주제학습 | 경제사냥꾼 영상 자막 | YouTube | RSS | Free | READY | 주제 선정 학습 | 이벤트 | 수집데이터 |
| 엔진로그 | anomaly_log | 내부 로직 | 파생 | Free | READY | 이상징후 기록 | 1일 | 파생데이터 |
| 주제선정 | topic_package | 내부 로직 | 파생 | Free | READY | 주제 자동 선정 | 1일 | 파생데이터 |
| 콘텐츠생성 | script.json | 내부 로직 | 파생 | Free | READY | 콘텐츠 생성 | 1일 | 파생데이터 |
