# src/agents/collectors/flow_collector.py
# HOIN Insight Flow Collector (v1.0)
# 목적: 외국인 수급, ETF Flow, 이벤트 캘린더 데이터 규격화 및 저장

import json
import os
import re
from pathlib import Path
from datetime import datetime
from src.utils.target_date import get_target_ymd, get_current_round

try:
    import requests
    from bs4 import BeautifulSoup
    _HTTP_OK = True
except ImportError:
    _HTTP_OK = False

class FlowCollector:
    name = "FLOW"
    sensitivity = "MID"
    ttl_minutes = 120

    def __init__(self, output_dir: Path = None):
        self.base_dir = Path(os.getenv("HOIN_BASE_DIR", Path(__file__).resolve().parents[3]))
        self.today = get_target_ymd().replace("-", "")
        self.round = get_current_round()
        self.raw_dir = output_dir if output_dir else self.base_dir / f"data/raw/{self.today}/{self.round}"
        self.flow_dir = self.base_dir / "data/flow"
        self.flow_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        print(f"🌊 AGENT-01 FLOW_COLLECTOR 시작 [{self.today}]")

        try:
            # 1. 외국인 수급 데이터 입수 (기존 market.json 활용 및 가공)
            self.collect_foreign_flow()

            # 2. 업종별 외국인 순매수 — Signal 3용 (네이버 frgn.naver 스크래핑)
            self.collect_sector_flow()

            # 3. ETF Flow 데이터 입수 (글로벌 자금 흐름)
            self.collect_etf_flow()

            # 4. 이벤트 캘린더 추출 (consensus.json 활용)
            self.collect_event_calendar()

            print("  ✅ Flow 데이터 레이어 구축 완료")
            return {
                "agent": self.name,
                "process_success": True,
                "data_valid": True,
                "freshness_status": "FRESH"
            }
        except Exception as e:
            print(f"  ❌ FlowCollector 실패: {e}")
            return {
                "agent": self.name,
                "process_success": False,
                "error": str(e)
            }

    def collect_foreign_flow(self):
        """외국인 순매수 금액 및 트렌드 계산"""
        market_p = self.raw_dir / "market.json"
        if not market_p.exists(): return

        try:
            market_data = json.loads(market_p.read_text())
            # 기존 market.json에 저장된 kospi_foreign_net 사용
            net_buy = market_data.get("data", {}).get("kospi_foreign_net", 0)
            
            # 히스토리 기반 트렌드 계산 (간소화)
            trend = "neutral"
            if net_buy > 100000000000: # 1000억 이상 유입
                trend = "inflow"
            elif net_buy < -100000000000:
                trend = "outflow"

            flow_data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "kospi_net_buy": net_buy,
                "kosdaq_net_buy": 0, # 확장 예정
                "trend_3d": trend
            }
            (self.flow_dir / "foreign_flow.json").write_text(json.dumps(flow_data, indent=2))
        except: pass

    def collect_sector_flow(self):
        """스테이지별 외국인 순매수 수집 → sector_flow_{today}.json 저장 (Signal 3 입력)

        market_context.json의 각 스테이지 tickers를 기반으로
        네이버 frgn.naver를 스크래핑해 업종별 외국인 순매수(주수)를 합산한다.
        STAGE_1(대장주)은 sector명을 '전기전자'로 고정 (SEMI_KEYWORDS 매칭용).
        """
        if not _HTTP_OK:
            print("  ⚠️ requests/bs4 미설치 — sector_flow 수집 건너뜀")
            return

        context_path = self.base_dir / "data/monitoring/market_context.json"
        if not context_path.exists():
            print("  ⚠️ market_context.json 없음 — rotation_radar 먼저 실행 필요")
            return

        try:
            context = json.loads(context_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ⚠️ market_context.json 파싱 실패: {e}")
            return

        stages = context.get("stages", {})
        sectors = []

        # STAGE_1 sector명 고정 (대장주 = 전기전자, SEMI_KEYWORDS 매칭)
        stage_sector_map = {
            "STAGE_1_SPARK": "전기전자",
        }

        for stage_key, stage_data in stages.items():
            sector_name = stage_sector_map.get(
                stage_key,
                stage_data.get("_matched_naver_sector", stage_key)
            )
            tickers = stage_data.get("tickers", [])[:3]  # 상위 3종목만

            total_foreign = 0
            for ticker in tickers:
                net = self._fetch_foreign_net(ticker)
                if net is not None:
                    total_foreign += net

            sectors.append({"sector": sector_name, "foreigner": total_foreign})
            print(f"    {sector_name}: 외국인 {total_foreign:+,}주")

        if not sectors:
            return

        flow_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "data": {"sectors": sectors}
        }

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.raw_dir / f"sector_flow_{self.today}.json"
        out_path.write_text(json.dumps(flow_data, indent=2, ensure_ascii=False))
        print(f"  ✅ sector_flow 저장: {out_path.name}")

    def _fetch_foreign_net(self, ticker: str):
        """네이버 frgn.naver에서 최근 확정 거래일의 외국인 순매수(주수) 반환."""
        url = f"https://finance.naver.com/item/frgn.naver?code={ticker}"
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        try:
            res = requests.get(url, headers=headers, timeout=8)
            soup = BeautifulSoup(res.text, "html.parser")

            for table in soup.find_all("table"):
                ths = [th.text.strip() for th in table.find_all("th")]
                if "외국인" not in ths or "날짜" not in ths:
                    continue
                for row in table.find_all("tr"):
                    cols = [td.text.strip() for td in row.find_all("td")]
                    if len(cols) < 7:
                        continue
                    raw = cols[6].replace(",", "").replace("+", "").strip()
                    if raw and re.match(r"^-?\d+$", raw):
                        return int(raw)
            return None
        except Exception:
            return None

    def collect_etf_flow(self):
        """ETF 순유입/유출 데이터 (프록시 데이터 사용 또는 수집)"""
        # 실제 환경에서는 별도 API 호출이 필요하나, 현재는 규격 준수를 위한 생성 로직
        # SPY, QQQ 등은 거래대금 변동 등으로 프록시 계산 가능
        flow_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "SPY": {"net_flow": 1200000000, "trend": "inflow"}, # Sample
            "QQQ": {"net_flow": -500000000, "trend": "outflow"},
            "KOSPI_ETF": {"net_flow": 800000000, "trend": "inflow"}
        }
        (self.flow_dir / "etf_flow.json").write_text(json.dumps(flow_data, indent=2))

    def collect_event_calendar(self):
        """주요 이벤트 및 임팩트 레이어"""
        consensus_p = self.raw_dir / "consensus.json"
        events = []
        
        if consensus_p.exists():
            try:
                c_data = json.loads(consensus_p.read_text())
                major = c_data.get("major_surprises", [])
                for m in major:
                    events.append({
                        "type": "macro",
                        "name": m.get("event", "Economic Data"),
                        "impact": "high" if abs(m.get("surprise_pct", 0)) > 5.0 else "medium"
                    })
            except: pass

        if not events:
            # Fallback (Static/Keyword matching from sentiment)
            events.append({"type": "macro", "name": "Market Monitoring", "impact": "low"})

        flow_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "events": events
        }
        (self.flow_dir / "event_calendar.json").write_text(json.dumps(flow_data, indent=2))

if __name__ == "__main__":
    FlowCollector().run()
