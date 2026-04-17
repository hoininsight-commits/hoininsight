import json
from datetime import datetime, timedelta
from pathlib import Path
from src.analytics.dynamic_scanner import DynamicScanner

class DynamicThemeScanner(DynamicScanner):
    """
    고도화된 선점형 테마 스캐너:
    1. Zero Cost: 기존 themes.json 매칭
    2. Anomaly Detection: 미분류 종목 3개 이상 포착
    3. AI Naming: 3일 이상 지속성 확인 시 Gemini 1회 호출
    """
    def __init__(self, 
                 themes_db_path="data/rrg/themes.json", 
                 history_path="data/rrg/history/volume_rank.json",
                 unidentified_history_path="data/rrg/history/unidentified_history.json"):
        super().__init__(themes_db_path, history_path)
        self.unidentified_history_path = Path(unidentified_history_path)
        self.unidentified_history_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 미분류 히스토리 로드
        if self.unidentified_history_path.exists():
            with open(self.unidentified_history_path, "r", encoding="utf-8") as f:
                self.unidentified_history = json.load(f)
        else:
            self.unidentified_history = {}

    def scan_with_radar(self):
        """선점형 레이더 필터링 로직"""
        print(f"📡 [Radar Scanner] Starting hybrid anomaly detection...")
        
        # 1. 시중 데이터 수집 및 1차 필터 (부모 클래스 활용)
        threshold_factor = self.calculate_market_factor()
        kospi_top = self.fetch_top_stocks(0)
        kosdaq_top = self.fetch_top_stocks(1)
        
        th_kospi = self.base_threshold_kospi * threshold_factor
        th_kosdaq = self.base_threshold_kosdaq * threshold_factor
        
        all_candidates = kospi_top + kosdaq_top
        today_str = datetime.now().strftime("%Y%m%d")
        
        # 히스토리 업데이트 (부모 클래스 메서드)
        self.update_history(today_str, all_candidates)
        
        # 2. 거래대금 + 지속성 필터링 (최소 20위권 내 3일 지속)
        filtered_stocks = []
        for s in all_candidates:
            if (s['market'] == 'KOSPI' and s['amount'] >= th_kospi) or (s['market'] == 'KOSDAQ' and s['amount'] >= th_kosdaq):
                if self.check_persistence(s['symbol'], top_n=20, days=3):
                    filtered_stocks.append(s)

        # 3. 하이브리드 매핑 (Zero Cost -> Anomaly)
        final_stocks = []
        unknown_stocks = []
        
        for s in filtered_stocks:
            # Step 1: Zero Cost 매칭
            if s['symbol'] in self.themes_db:
                s['theme'] = self.themes_db[s['symbol']]
                final_stocks.append(s)
            else:
                unknown_stocks.append(s)
        
        # 4. 이상 탐지 (Step 2 & 3)
        if len(unknown_stocks) >= 3:
            print(f"📈 [Radar] Detecting Anomaly: {len(unknown_stocks)} unidentified stocks found.")
            
            # 3일 연속 지속성 확인을 위해 오늘치 저장
            self.unidentified_history[today_str] = [s['symbol'] for s in unknown_stocks]
            self.maintenance_unidentified_history()
            
            # 지속성 확인 (오늘 포함 과거 3일간 3개 이상 미분류 종목 수급 유입)
            if self.check_unidentified_persistence(days=3, min_count=3):
                print(f"🤖 [Radar] Triggering AI Naming for new persistent group...")
                # Step 3: AI Naming (1회 호출)
                stock_names = [s['name'] for s in unknown_stocks]
                new_theme_name = self.naming_new_theme(stock_names)
                
                # DB 업데이트
                for s in unknown_stocks:
                    s['theme'] = new_theme_name
                    self.themes_db[s['symbol']] = new_theme_name
                    final_stocks.append(s)
                
                self.save_themes_db()
            else:
                print(f"⏳ [Radar] Not persistent enough yet. Tagging as '신규수급_관찰'.")
                for s in unknown_stocks:
                    s['theme'] = "신규수급_관찰"
                    final_stocks.append(s)
        else:
            # 개별 미분류 종목들은 일단 '기타' 처리 (노이즈 제거)
            for s in unknown_stocks:
                s['theme'] = "기타_미분류"
                final_stocks.append(s)

        # 저장
        self.save_unidentified_history()
        
        # 테마별 그룹화
        themes_group = {}
        for s in final_stocks:
            t = s['theme']
            if t not in themes_group:
                themes_group[t] = []
            themes_group[t].append(s)
            
        return themes_group

    def check_unidentified_persistence(self, days=3, min_count=3):
        """최근 N일간 미분류 종목 수급이 유의미한 규모인지 확인"""
        dates = sorted(self.unidentified_history.keys(), reverse=True)
        if len(dates) < days: return False
        
        check_dates = dates[:days]
        for d in check_dates:
            if len(self.unidentified_history[d]) < min_count:
                return False
        return True

    def naming_new_theme(self, stock_names):
        """Gemini를 호출하여 신규 집해된 종목군에 테마명 부여 (1회 호출)"""
        prompt = f"""
        최근 시장에서 동시에 수급이 몰리는 신규 종목 그룹입니다: {', '.join(stock_names)}
        이 종목들의 공통적인 산업적 키워드나 테마명을 2~3단어로 요약해서 하나만 알려줘.
        예: '초거대 AI 반도체', '원전 수출 컨소시엄', '우주항공 방산'.
        반드시 테마명만 출력해라.
        """
        try:
            new_theme = self.gemini.call(prompt).strip()
            new_theme = new_theme.replace("`", "").replace("*", "").strip()
            return new_theme if new_theme else "신규_미분류"
        except:
            return "신규_미분류"

    def maintenance_unidentified_history(self):
        """최근 10일치 히스토리만 유지"""
        dates = sorted(self.unidentified_history.keys(), reverse=True)
        if len(dates) > 10:
            for d in dates[10:]:
                del self.unidentified_history[d]

    def save_unidentified_history(self):
        with open(self.unidentified_history_path, "w", encoding="utf-8") as f:
            json.dump(self.unidentified_history, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scanner = DynamicThemeScanner()
    res = scanner.scan_with_radar()
    from pprint import pprint
    pprint(res)
