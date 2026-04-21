# Identification: Cache Policy Issues — HOIN Insight (#080-TASK-3)

This document details the specific technical flaws discovered in the current caching architecture and their negative impact on the engine's narrative reliability.

## 🚩 1. 고민감도(HIGH) 데이터에 대한 강력한 일일 캐시
- **코드 위치**: `src/agents/collectors/collector_runner.py:53-61`
- **문제점**: `cache_file.exists()`만 확인하여 당일 파일이 존재하면 무조건 수집을 건너뜀.
- **Why Now 왜곡**: 
    - 아침 9시에 수집된 뉴스 헤드라인이 오후 4시의 폭락 장세에서도 "오늘의 뉴스"로 활용됨.
    - 오후에 터진 '블랙 스완' 이벤트를 엔진이 아예 인지하지 못하는 "장님 파이프라인" 현상 발생.

## 🚩 2. "성공으로 위장한 Stale" — 하드코딩 Fallback
- **코드 위치**: `src/agents/collector.py:507` (`_get_fear_greed` 메서드)
- **문제점**: API 호출 실패 시 `return 25.0` (공포 단계)을 하드코딩하여 반환함.
- **Why Now 왜곡**: 
    - 실제 시장은 탐욕(75.0) 상태인데, 통신 장애로 인해 엔진이 시장을 공포(25.0)로 오판하고 "공포를 사야 할 때"라는 잘못된 내러티브를 생성함.
    - 최소한 'UNKNOWN' 상태를 반환하거나 캐시를 무효화해야 함.

## 🚩 3. 데이터 Freshness 검증 부재 (Size-Only Check)
- **코드 위치**: `src/agents/collectors/collector_runner.py:57`
- **문제점**: `if cache_file.stat().st_size > 100` 로직으로 파일 크기만 보고 유효성을 판단함.
- **Why Now 왜곡**: 
    - 데이터가 0바이트로 깨지지만 않았을 뿐, 그 내용이 얼마나 노후화되었는지는 전혀 고려하지 않음.
    - "성공 처리되었지만 실제로는 Stale 데이터"인 전형적인 케이스.

## 🚩 4. Market 데이터의 정적 히스토리화
- **코드 위치**: `src/agents/collector.py:476-478`
- **문제점**: `history/market_90d.json` 폴더에 데이터를 저장할 때, 당일 최신 변동분을 실시간으로 덮어쓰지 않고 정적 파일로 관리될 가능성.
- **Why Now 왜곡**: 
    - `Detector`나 `Analyst`가 참조하는 히스토리 데이터가 장중 최신가를 반영하지 못해, 추세 전환 포인트를 놓치게 됨.

## 🚩 5. RSS 소스 차단 시 대응력 부재
- **코드 위치**: `src/agents/collector.py:566-580`
- **문제점**: 특정 RSS 피드(Bloomberg 등) 차단 시 대체 소스(WSJ)가 있지만, 캐시 정책 때문에 한 번 수집 실패(또는 빈 결과)가 캐시되면 하루 종일 빈 뉴스로 작동함.
- **Why Now 왜곡**: 
    - 수집 실패로 인해 뉴스 데이터가 부족해도 캐시 때문에 재시도하지 않음 -> 결과적으로 "아무 일 없는 시장"으로 잘못 해석됨.
