# HOIN Insight 샘플 산출물 경로 정리 (Output Samples)
v1.0 | 2026-04-20 감사 수행

## 1. 최근 7일 주요 산출물 경로 (SSOT 기준)

본 레포지토리의 가장 최근(2026-04-19) 실행 기준 데이터입니다.

| 데이터 종류 | 파일 경로 (Repo Path) | 용도 | 소비 에이전트 |
| :--- | :--- | :--- | :--- |
| **Market Raw** | `data/raw/history/market_90d.json` | 90일 히스토리 및 Z-score 계산 원천 | Detector, Analyst |
| **Today Signal** | `data/signals/20260419/today_signal.json` | 최종 선정된 오늘의 신호 | Analyst, Writer |
| **Analysis** | `data/analysis/20260419/today_analysis.json` | 3계층 문장이 포함된 심층 분석 | Writer |
| **Stocks** | `data/analysis/20260419/today_stocks.json` | 토픽과 연결된 유효 종목 리스트 | Writer, Dashboard |
| **Final Script** | `data/scripts/20260419/today_script_long.md` | 최종 유튜브 롱폼 스크립트 | Publisher |
| **Publish Meta**| `docs/today_data.json` | **대시보드 SSOT** (전체 데이터 합본) | Dashboard UI |
| **Archive Index**| `docs/topics/index.json` | 과거 모든 토픽의 메타데이터 인덱스 | Dashboard Archive |
| **Signal Log** | `data/history/signal_log.json` | 전체 수집 기간의 시그널 누적 로그 | Publisher, Auditor |

## 2. 대표 샘플 미리보기 (today_data.json)

```json
{
  "last_updated": "2026-04-19T21:55:16...",
  "today": {
    "date": "2026-04-19",
    "signal": {
      "topic": "뉴스 악재 속 지수 상승 (Price-News 모순)",
      "anomaly_type": "NEWS_MISMATCH",
      "strength": 9.2,
      "why_now": "악재를 압도하는 수급 또는 선반영... 뉴스 트리거: Stocks Sink in Broad AI Rout..."
    },
    "market_state": {
      "risk_appetite": "상승",
      "hedging_activity": "감소",
      "conviction": "높음"
    },
    "z_scores": {
      "SP500": 1.96,
      "WTI": -1.93,
      "Gold": 1.52,
      "DXY": -1.51,
      "VIX": -1.43
    }
  }
}
```

## 3. 중간 산출물 성격 정의 (Intermediate Artifacts)
- **`data/raw/history/`**: 영구 보관되는 시계열 데이터.
- **`data/signals/`**: 주제 선정의 경쟁 과정을 담은 분석 전 단계 데이터.
- **`data/analysis/`**: AI가 종목과 섹터 사이를 브릿징한 기술 문서.
- **`data/scripts/`**: 방송용 페르소나와 팩트체크 리포트를 담은 최종 제작 준비물.
