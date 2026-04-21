# Recommendation: Redesigned Cache Policy — HOIN Insight (#080-TASK-4)

This document defines the new operational standards for data collection, shifting from a daily static cache to a sensitivity-aware dynamic cache.

## 🛠 표준 캐시 정책 정의

| 분류 | 대상 데이터 | 권장 TTL | 수집 주기 | Stale 허용 여부 | 재수집(Invalidation) 조건 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **고민감도 (HIGH)** | RSS 뉴스, Sentiment, VIX, Fear&Greed | **30분** | 1시간 이내 | **NO** | 30분 초과 시 무조건 재수집 |
| **중간 민감도 (MID)** | Market 가격, DXY, US10Y, DART 공시 | **2시간** | 장중 3~4회 | **Partial** | 장중 2시간 초과 시 재수집 |
| **저빈도 구조 (LOW)** | FRED/ECOS 거시지표, COT Data | **12시간** | 일 1~2회 | **YES** | 12시간 초과 시 재수집 |

## 🎯 데이터 소스별 상세 가이드라인

### 1. RSS 뉴스 (Critical Why Now)
- **정책**: `CONDITIONAL` (항상 신선도 유지)
- **TTL**: 30분
- **Stale Detection**: 파일 내 `collected_at`이 현재 시간보다 30분 이상 과거면 캐시 무시.
- **Cache Hit 여부**: 30분 이내일 때만 `True`.

### 2. 시장 가격 및 지수 (Market Context)
- **정책**: `YES` (다만 장중 동적 TTL 적용)
- **TTL**: 60분 (장중), 12시간 (장마감 후)
- **Requirement**: "장중 가격 발작"을 감지하기 위해 최소 1시간 단위의 신선도 요구.

### 3. DART 공시 (Event Trigger)
- **정책**: `CONDITIONAL`
- **TTL**: 1시간
- **Invalidation**: 뉴스에서 특정 기업이 언급될 경우, 해당 기업 기반 DART 캐시를 즉시 무효화하고 재수집.

## 🚀 "WHY NOW" 실시간 유지 데이터 리스트
아래 데이터는 시스템 구동 시 캐시 상태와 상관없이 **반드시 신선함을 검증**해야 합니다:
1. **WSJ / CNBC Markets RSS Feed**
2. **Fear & Greed Index**
3. **KOSPI / SP500 현재가**
4. **WTI 유가**

## 💡 시스템 표준 원칙
1. **Timestamp First**: 파일 존재 여부가 아니라, 파일 내부의 '수집 시각'을 제1 판단 근거로 삼는다.
2. **Graceful Stale**: API 장애 시에만 Stale 데이터를 사용하되, 반드시 `freshness_status = STALE` 플래그를 달아 엔진에게 알린다.
3. **Explicit Unknown**: 하드코딩된 Fallback(예: 25.0) 대신 `None` 또는 `UNKNOWN`을 사용하여 데이터 왜곡을 방지한다.
