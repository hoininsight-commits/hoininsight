# src/agents/collectors/financial_collectors.py

import json
import requests
import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from src.agents.collector import CollectorAgent

class ConsensusCollector(CollectorAgent):
    """[RESTORED] Wrapper for Consensus data collection"""
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.today = datetime.now().strftime("%Y%m%d")
        self.name = "ConsensusCollector"
        self.ttl_minutes = 720
        self.sensitivity = "LOW"

    def run(self) -> dict:
        try:
            data = self.collect_consensus()
            return {
                "process_success": True,
                "data_valid": True,
                "freshness_status": "FRESH"
            }
        except Exception as e:
            return {"process_success": False, "error": str(e)}

class COTCollector(CollectorAgent):
    """COT (Commitment of Traders) — CFTC 공개 데이터 + yfinance 포지션 프록시"""
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.today = datetime.now().strftime("%Y%m%d")
        self.name = "COTCollector"
        self.ttl_minutes = 1440
        self.sensitivity = "LOW"

    def run(self) -> dict:
        print("📊 COT 포지션 데이터 수집 중...")
        try:
            data = self._fetch_cot()
            result = self._wrap_data(data, ttl_minutes=self.ttl_minutes)
            output_path = self.output_dir / "cot.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"  ✅ COT 저장 — S&P순포지션:{data.get('sp500_net_pct')}% 금:{data.get('gold_net_pct')}% 원유:{data.get('oil_net_pct')}%")
            return {"process_success": True, "data_valid": True, "freshness_status": "FRESH"}
        except Exception as e:
            print(f"  ⚠️ COT 수집 실패: {e}")
            return {"process_success": False, "error": str(e)}

    def _fetch_cot(self) -> dict:
        import yfinance as yf
        import zipfile, io, csv

        # ── 1. CFTC Disaggregated Futures-Only (현년도 zip) ──
        year = datetime.now().year
        cot_url = f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip"
        targets = {
            "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE": "sp500",
            "GOLD - COMMODITY EXCHANGE INC.":               "gold",
            "CRUDE OIL, LIGHT SWEET - COMMODITY EXCHANGE":  "crude_oil",
            "U.S. DOLLAR INDEX - ICE FUTURES U.S.":         "usd_index",
        }
        positions = {}
        try:
            resp = requests.get(cot_url, timeout=20)
            if resp.ok:
                with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                    fname = [n for n in z.namelist() if n.endswith(".txt")][0]
                    lines = z.read(fname).decode("utf-8", errors="ignore").splitlines()
                reader = csv.DictReader(lines)
                latest = {}  # market_name -> latest row
                for row in reader:
                    mkt = row.get("Market and Exchange Names", "").strip().upper()
                    for key in targets:
                        if key in mkt:
                            # 날짜 기준 최신 행만 유지
                            prev = latest.get(key)
                            if prev is None or row.get("As of Date in Form YYYY-MM-DD","") >= prev.get("As of Date in Form YYYY-MM-DD",""):
                                latest[key] = row
                for key, alias in targets.items():
                    row = latest.get(key)
                    if row:
                        try:
                            longs  = float(row.get("NonComm_Positions_Long_All", 0) or 0)
                            shorts = float(row.get("NonComm_Positions_Short_All", 0) or 0)
                            total  = longs + shorts
                            net_pct = round((longs - shorts) / total * 100, 1) if total > 0 else None
                            positions[alias] = {
                                "long": int(longs),
                                "short": int(shorts),
                                "net": int(longs - shorts),
                                "net_pct": net_pct,
                                "report_date": row.get("As of Date in Form YYYY-MM-DD", ""),
                            }
                        except Exception:
                            pass
        except Exception as e:
            print(f"  ⚠️ CFTC zip 수집 실패: {e} — yfinance 프록시로 전환")

        # ── 2. yfinance 프록시 (CFTC 실패 시 또는 보완) ──
        proxy_tickers = {
            "sp500":     ("ES=F",  "^VIX"),
            "gold":      ("GC=F",  None),
            "crude_oil": ("CL=F",  None),
            "usd_index": ("DX=F",  None),
        }
        for alias, (ticker, aux) in proxy_tickers.items():
            if alias in positions:
                continue  # CFTC 성공 시 스킵
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="5d")
                if not hist.empty:
                    last = hist.iloc[-1]
                    prev = hist.iloc[-2] if len(hist) > 1 else last
                    chg_pct = round((last["Close"] - prev["Close"]) / prev["Close"] * 100, 2)
                    vol_ratio = round(last["Volume"] / hist["Volume"].mean(), 2) if hist["Volume"].mean() > 0 else 1.0
                    # 가격 방향 + 거래량으로 순포지션 대리 추정
                    estimated_net_pct = round(chg_pct * vol_ratio * 10, 1)
                    positions[alias] = {
                        "price": round(float(last["Close"]), 2),
                        "change_pct": chg_pct,
                        "volume_ratio": vol_ratio,
                        "estimated_net_pct": max(-100, min(100, estimated_net_pct)),
                        "source": "yfinance_proxy",
                    }
            except Exception:
                pass

        # ── 3. 종합 센티먼트 판정 ──
        sp = positions.get("sp500", {})
        gold = positions.get("gold", {})
        oil = positions.get("crude_oil", {})

        sp_net = sp.get("net_pct") or sp.get("estimated_net_pct") or 0
        gold_net = gold.get("net_pct") or gold.get("estimated_net_pct") or 0

        if sp_net > 20:
            sentiment = "BULLISH"
        elif sp_net < -20:
            sentiment = "BEARISH"
        elif gold_net > 30:
            sentiment = "RISK-OFF (금 피난처 수요)"
        else:
            sentiment = "NEUTRAL"

        return {
            "date": self.today,
            "source": "CFTC/yfinance",
            "market_sentiment": sentiment,
            "sp500_net_pct":   sp.get("net_pct") or sp.get("estimated_net_pct"),
            "gold_net_pct":    gold.get("net_pct") or gold.get("estimated_net_pct"),
            "oil_net_pct":     oil.get("net_pct") or oil.get("estimated_net_pct"),
            "positions":       positions,
        }

class ECOSCollector(CollectorAgent):
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.today = datetime.now().strftime("%Y%m%d")
        self.name = "ECOSCollector"
        self.ttl_minutes = 360
        self.sensitivity = "MID"
    def run(self) -> dict:
        try:
            self.collect_ecos()
            return {"process_success": True, "data_valid": True, "freshness_status": "FRESH"}
        except Exception as e:
            return {"process_success": False, "error": str(e)}

class DARTCollector(CollectorAgent):
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.today = datetime.now().strftime("%Y%m%d")
        self.name = "DARTCollector"
        self.ttl_minutes = 120
        self.sensitivity = "HIGH"
    def run(self) -> dict:
        try:
            self.collect_dart()
            return {"process_success": True, "data_valid": True, "freshness_status": "FRESH"}
        except Exception as e:
            return {"process_success": False, "error": str(e)}

class MarketBreadthCollector(CollectorAgent):
    """[NEW] Market Breadth Collector (No-Browser Version)
    Captures advancing/declining stock counts to detect rotation signals.
    """
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.today = datetime.now().strftime("%Y%m%d")
        self.name = "MarketBreadthCollector"
        self.ttl_minutes = 60 # 장중에는 자주 체크
        
    def run(self) -> dict:
        print(f"📡 시장폭(Market Breadth) 데이터 수집 중... (브라우저 미사용)")
        try:
            data = self.collect_breadth()
            
            # 신호 판정 로직 (1단계: 순환매 포착)
            for market in ["KOSPI", "KOSDAQ"]:
                m_data = data["markets"][market]
                up = m_data["advancing"]
                down = m_data["declining"]
                
                # 조건: 상승 > 하락 * 2 (RotationConfirmationEngine과 동일 기준)
                ratio = round(up / down, 2) if down > 0 else 0.0
                if down > 0 and up > down * 2:
                    m_data["signal_1_detected"] = True
                    m_data["message"] = f"🔥 {market} 순환매 1단계 신호 포착! (상승 {up} / 하락 {down}, 비율 {ratio}x)"
                else:
                    m_data["signal_1_detected"] = False
                    m_data["message"] = f"대장주 독주 또는 관망 구간 (상승 {up} / 하락 {down}, 비율 {ratio}x)"
                m_data["ratio"] = ratio

            # 데이터 저장
            result = self._wrap_data(data, ttl_minutes=self.ttl_minutes)
            output_path = self.output_dir / f"market_breadth_{self.today}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return {
                "process_success": True,
                "data_valid": True,
                "freshness_status": "FRESH",
                "signals": {m: data["markets"][m]["signal_1_detected"] for m in ["KOSPI", "KOSDAQ"]}
            }
        except Exception as e:
            print(f"❌ 시장폭 수집 에러: {e}")
            return {"process_success": False, "error": str(e)}

    def collect_breadth(self) -> dict:
        results = {"date": self.today, "markets": {}}
        headers = {"User-Agent": "Mozilla/5.0"}
        
        for market in ["KOSPI", "KOSDAQ"]:
            url = f"https://finance.naver.com/sise/sise_index.naver?code={market}"
            resp = requests.get(url, headers=headers)
            resp.encoding = 'cp949'
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Naver 구조: <li class="lst2">...<span>638</span>...</li> (상승)
            # <li class="lst4">...<span>242</span>...</li> (하락)
            
            up_li = soup.find("li", class_="lst2")
            down_li = soup.find("li", class_="lst4")
            
            advancing = 0
            declining = 0
            
            if up_li:
                # '상승종목수' 텍스트 뒤의 숫자가 담긴 span을 찾음
                up_span = up_li.find_all("span")[-1]
                if up_span:
                    advancing = int(re.sub(r"[^0-9]", "", up_span.get_text()))
            if down_li:
                # '하락종목수' 텍스트 뒤의 숫자가 담긴 span을 찾음
                down_span = down_li.find_all("span")[-1]
                if down_span:
                    declining = int(re.sub(r"[^0-9]", "", down_span.get_text()))
            
            # 지수 값 추출
            now_val = soup.find("em", id="now_value")
            index_price = now_val.get_text() if now_val else "0"
            
            results["markets"][market] = {
                "index": index_price,
                "advancing": advancing,
                "declining": declining,
                "ratio": round(advancing / declining, 2) if declining > 0 else 0
            }
            
        return results

class SectorFlowCollector(CollectorAgent):
    """[NEW] Investor Flow by Sector (Foreigner/Institutional)
    Tracks where the smart money is moving between industries.
    """
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.today = datetime.now().strftime("%Y%m%d")
        self.name = "SectorFlowCollector"
        self.ttl_minutes = 120

    def run(self) -> dict:
        print("💰 투자자별 업종 수급 흐름 분석 중...")
        try:
            data = self.collect_flow()
            
            # 분석: 전체 업종 수급 유입 체크
            flow_summary = []
            
            for item in data[:15]: # 상위 15개 업종 분석
                sector_name = item["sector"]
                f_flow = item["foreigner"]
                i_flow = item["institutional"]
                
                # 순환매 신호: 외국인 & 기관 동반 매수 (쌍끌이)
                if f_flow > 0 and i_flow > 0:
                    flow_summary.append(f"✨ {sector_name}: 외국인/기관 쌍끌이 매수 중")
                elif f_flow > 100: # 외국인 집중 매수 (단위: 억 단위 가정)
                    flow_summary.append(f"🌊 {sector_name}: 외국인 집중 유입")

            result = self._wrap_data({"sectors": data, "summary": flow_summary}, ttl_minutes=self.ttl_minutes)
            output_path = self.output_dir / f"sector_flow_{self.today}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                
            return {"process_success": True, "data_valid": True, "summary": flow_summary}
        except Exception as e:
            print(f"❌ 수급 분석 오류: {e}")
            return {"process_success": False, "error": str(e)}

    def collect_flow(self) -> list:
        # 네이버 금융 업종별 투자자 매수 현황 (KOSPI 기준 sosok=0)
        url = "https://finance.naver.com/sise/sise_trans_stat.naver?sosok=0"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers)
        resp.encoding = 'cp949'
        soup = BeautifulSoup(resp.text, "html.parser")
        
        table = soup.find("table", class_="type_1")
        rows = table.find_all("tr")
        
        sector_data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 6:
                name_tag = cols[0].find("a")
                if name_tag:
                    name = name_tag.get_text().strip()
                    # 외국인(cols[4]), 기관(cols[5]) 순매수량 (단위: 억)
                    # 실제 네이버 구조에 따라 인덱스 확인 필요 (보통 4, 5번이 외인/기관)
                    try:
                        def parse_val(txt):
                            return float(re.sub(r"[^0-9.-]", "", txt))
                        
                        f_net = parse_val(cols[4].get_text())
                        i_net = parse_val(cols[5].get_text())
                        
                        sector_data.append({
                            "sector": name,
                            "foreigner": f_net,
                            "institutional": i_net
                        })
                    except: continue
        return sector_data


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from src.utils.target_date import get_standard_path_prefix
    out = Path("data/raw") / get_standard_path_prefix()
    out.mkdir(parents=True, exist_ok=True)
    agent = sys.argv[1] if len(sys.argv) > 1 else "all"
    if agent in ("consensus", "all"):
        ConsensusCollector(out).run()
    if agent in ("cot", "all"):
        COTCollector(out).run()
