import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path
from src.core.gemini_client import GeminiClient

class DynamicScanner:
    def __init__(self, themes_db_path="data/rrg/themes.json", history_path="data/rrg/history/volume_rank.json"):
        self.themes_db_path = Path(themes_db_path)
        self.history_path = Path(history_path)
        self.base_threshold_kospi = 50_000_000_000 # 500억
        self.base_threshold_kosdaq = 30_000_000_000 # 300억
        
        self.gemini = GeminiClient()
        
        # 테마 DB 로드
        if self.themes_db_path.exists():
            with open(self.themes_db_path, "r", encoding="utf-8") as f:
                self.themes_db = json.load(f)
        else:
            self.themes_db = {}
            
        # 히스토리 로드
        if self.history_path.exists():
            with open(self.history_path, "r", encoding="utf-8") as f:
                self.history = json.load(f)
        else:
            self.history = {"last_update": "", "rankings": {}}

    def fetch_top_stocks(self, sosok=0):
        """네이버 금융 거래상위 100위 수집 (sosok 0: KOSPI, 1: KOSDAQ)"""
        url = f"https://finance.naver.com/sise/sise_quant.naver?sosok={sosok}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        res.encoding = 'euc-kr'
        soup = BeautifulSoup(res.text, 'lxml')
        
        stocks = []
        table = soup.find('table', class_='type_2')
        if not table: return []
        
        rows = table.find_all('tr')
        rank = 1
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 11: continue
            
            try:
                name_tag = cols[1].find('a')
                if not name_tag: continue
                
                name = name_tag.text.strip()
                code = name_tag['href'].split('=')[-1]
                symbol = f"{code}.KS" if sosok == 0 else f"{code}.KQ"
                
                price = int(cols[2].text.replace(',', ''))
                volume = int(cols[5].text.replace(',', '')) # 거래량
                amount = int(cols[6].text.replace(',', '')) * 1_000_000 # 거래대금(백만 단위)
                
                stocks.append({
                    "rank": rank,
                    "symbol": symbol,
                    "name": name,
                    "amount": amount,
                    "market": "KOSPI" if sosok == 0 else "KOSDAQ"
                })
                rank += 1
            except Exception as e:
                continue
                
        return stocks

    def scan(self):
        """실시간 스캐닝 및 필터링"""
        print(f"🔍 [Scanner] Scanning KOSPI and KOSDAQ top 100...")
        
        # 시장 연동형 Threshold factor 계산 (%)
        threshold_factor = self.calculate_market_factor()
        
        kospi_top = self.fetch_top_stocks(0)
        kosdaq_top = self.fetch_top_stocks(1)
        
        # 적용 Threshold 계산
        th_kospi = self.base_threshold_kospi * threshold_factor
        th_kosdaq = self.base_threshold_kosdaq * threshold_factor
        
        print(f"📊 [Scanner] Applied Threshold: KOSPI {th_kospi/1e8:.0f}억, KOSDAQ {th_kosdaq/1e8:.0f}억 (Factor: {threshold_factor:.2f})")
        
        all_candidates = kospi_top + kosdaq_top
        
        # 1. 1차 필터: 거래대금 하한선
        filtered = [s for s in all_candidates if (s['market'] == 'KOSPI' and s['amount'] >= th_kospi) or (s['market'] == 'KOSDAQ' and s['amount'] >= th_kosdaq)]
        
        # 2. 히스토리 업데이트 및 Persistence Filter 적용
        today_str = datetime.now().strftime("%Y%m%d")
        self.update_history(today_str, all_candidates)
        
        # 3일 연속 상위 20위 유지 종목 선별
        final_stocks = []
        for s in filtered:
            if self.check_persistence(s['symbol'], top_n=20, days=3):
                # 테마 매칭 (Hybrid Labeling)
                theme = self.get_theme(s['symbol'], s['name'])
                s['theme'] = theme
                final_stocks.append(s)
        
        # 테마별 그룹화
        themes_group = {}
        for s in final_stocks:
            t = s['theme']
            if t not in themes_group:
                themes_group[t] = []
            themes_group[t].append(s)
            
        print(f"✅ [Scanner] Found {len(final_stocks)} persistent stocks across {len(themes_group)} themes.")
        return themes_group

    def update_history(self, date_str, current_stocks):
        """랭킹 히스토리 갱신 (최근 10일치 보관)"""
        if self.history["last_update"] == date_str:
            return
            
        new_rankings = self.history.get("rankings", {})
        new_rankings[date_str] = {s['symbol']: s['rank'] for s in current_stocks}
        
        # 10일 이전 데이터 삭제
        dates = sorted(new_rankings.keys(), reverse=True)
        if len(dates) > 10:
            for d in dates[10:]:
                del new_rankings[d]
                
        self.history["last_update"] = date_str
        self.history["rankings"] = new_rankings
        
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def check_persistence(self, symbol, top_n=20, days=3):
        """최근 N일간 상위 M위 이내 유지 여부"""
        rankings = self.history.get("rankings", {})
        dates = sorted(rankings.keys(), reverse=True)
        
        if len(dates) < days: return True # 데이터가 쌓이기 전에는 통과
        
        check_dates = dates[:days]
        for d in check_dates:
            rank = rankings[d].get(symbol, 999)
            if rank > top_n:
                return False
        return True

    def get_theme(self, symbol, name):
        """Hybrid Theme Labeling: DB 조회 -> (없으면) Gemini"""
        # 1. DB 우선 조회
        if symbol in self.themes_db:
            return self.themes_db[symbol]
            
        # 2. 신규 종목의 경우 Gemini 호출
        print(f"🤖 [Scanner] Labeling new stock: {name} ({symbol})")
        prompt = f"""
        한국 주식 종목 '{name} ({symbol})'의 현재 주도적인 테마 키워드를 2~3단어로 알려줘.
        예: 인공지능 반도체, 2차전지 소재, 초전도체, 저PBR 금융.
        반드시 테마명만 출력해라. 다른 설명이나 마크다운은 생략한다.
        """
        try:
            new_theme = self.gemini.call(prompt).strip()
            # 마크다운 등 노이즈 제거
            new_theme = new_theme.replace("`", "").replace("*", "").strip()
            if not new_theme or len(new_theme) > 20: 
                new_theme = "미분류"
        except:
            new_theme = "미분류"
        
        # 3. DB 업데이트 및 즉시 저장
        self.themes_db[symbol] = new_theme
        self.save_themes_db()
        
        return new_theme

    def calculate_market_factor(self):
        """시장 전체 거래대금이 줄어들면 Threshold 하향 조정 (최소 0.8)"""
        # 기본값은 1.0 (정상 상황)
        # 시장 전체 거래대금이 감소한 '거래 절벽' 상황에서 하한선을 20% 낮춤
        # TODO: 실제 시장 총 거래대금 크롤링 연동
        return 1.0 

    def save_themes_db(self):
        with open(self.themes_db_path, "w", encoding="utf-8") as f:
            json.dump(self.themes_db, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scanner = DynamicScanner()
    themes = scanner.scan()
    for t, stocks in themes.items():
        print(f"Theme: {t} -> {[s['name'] for s in stocks]}")
