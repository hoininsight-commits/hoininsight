import os
import json
import pandas as pd
from pykrx import stock
import OpenDartReader
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# .env 로드
load_dotenv()

class RotationRadar:
    """[v4.0] AGNOSTIC DYNAMIC ROTATION RADAR"""
    
    def __init__(self):
        self.api_key = os.environ.get("OPENDART_API_KEY") or os.environ.get("DART_API_KEY")
        if not self.api_key:
            print("  ⚠️ OPENDART_API_KEY가 설정되지 않음. DART 수집을 건너뜁니다.")
            self.dart = None
            return
        self.dart = OpenDartReader(self.api_key)
        self.context_path = Path("data/monitoring/market_context.json")
        self.output_path = Path("data/monitoring/rotation_radar.json")
        self.breadth_dir = Path("data/raw") 
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def load_dynamic_context(self):
        if not self.context_path.exists():
            return {}
        return json.loads(self.context_path.read_text(encoding='utf-8'))

    def get_stage_color(self, stage_id):
        colors = {
            "STAGE_1_SPARK": "#00f2ff",
            "STAGE_2_SKELETON": "#00ff88",
            "STAGE_3_BODY": "#ffea00",
            "STAGE_4_SOUL": "#ff8800",
            "STAGE_5_TAIL": "#ff007a"
        }
        return colors.get(stage_id, "#ffffff")

    def get_real_signals(self, stages, days=3):
        print(f"📡 DART 신호 분석 중 (최근 {days}일)...")
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        signals = {}
        try:
            df = self.dart.list(start=start_date, end=end_date)
            if df is not None and not df.empty:
                target_reports = df[df['report_nm'].str.contains('공급계약|시설투자|수주', na=False)]
                for _, row in target_reports.iterrows():
                    title = row['report_nm']
                    company = row['corp_name']
                    
                    for stage_id, info in stages.items():
                        if any(kw.lower() in title.lower() or kw.lower() in company.lower() for kw in info['keywords']):
                            if stage_id not in signals: signals[stage_id] = []
                            signals[stage_id].append({
                                "company": company,
                                "title": title,
                                "date": row['rcept_dt'],
                                "link": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row['rcept_no']}"
                            })
        except Exception as e:
            print(f"  ❌ DART 수집 오류: {e}")
        return signals

    def get_market_breadth_stats(self):
        print("📊 시장폭 트렌드 분석...")
        breadth_files = sorted(list(self.breadth_dir.glob("**/market_breadth_*.json")), reverse=True)
        stats = {"today_ratio": 0.0, "today_adv": 0, "today_dec": 0, "streak_days": 0, "status": "IDLE", "message": "-"}
        history = []
        for f in breadth_files[:5]:
            try:
                d = json.loads(f.read_text(encoding='utf-8'))
                m = d.get("data", {}).get("markets", {}).get("KOSPI", {})
                if m: history.append(m)
            except: continue

        if history:
            latest = history[0]
            stats.update({"today_adv": latest.get("advancing", 0), "today_dec": latest.get("declining", 0), "today_ratio": latest.get("ratio", 0.0)})
            streak = 0
            for h in history:
                if h.get("advancing", 0) > h.get("declining", 0): streak += 1
                else: break
            stats["streak_days"] = streak
            if stats["today_ratio"] > 2.0: stats["status"], stats["message"] = "EXPANSION", f"시장폭 확장 중 ({stats['today_ratio']}배)"
            if streak >= 3: stats["status"], stats["message"] = "CONFIRMED", "순환매 본격화 확정 (3일 연속)"
        return stats

    def get_flow_timeline(self, stages_config, days=15):
        print(f"🌊 타임라인 분석 중...")
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        timeline = []
        try:
            stage_series = {}
            for sid, info in stages_config.items():
                tickers = info.get("tickers", [])
                changes = []
                for t in tickers:
                    try:
                        df = stock.get_market_ohlcv_by_date(start_date, end_date, t)
                        if not df.empty: changes.append(df['등락률'])
                    except: continue
                if changes: stage_series[sid] = pd.concat(changes, axis=1).mean(axis=1)
            
            if stage_series:
                df_flow = pd.DataFrame(stage_series).tail(days).fillna(0)
                for date, row in df_flow.iterrows():
                    timeline.append({"date": date.strftime("%m/%d"), "values": row.to_dict()})
        except Exception as e: print(f"  ❌ 타임라인 오류: {e}")
        return timeline

    def run(self):
        context = self.load_dynamic_context()
        if not context: return
        stages_config = context.get("stages", {})
        
        signals = self.get_real_signals(stages_config)
        breadth_stats = self.get_market_breadth_stats()
        flow_timeline = self.get_flow_timeline(stages_config)
        
        today_str = datetime.now().strftime('%Y%m%d')
        tracking_data = {}
        for sid, info in stages_config.items():
            tickers = info.get("tickers", [])
            stocks_info = []
            for t in tickers:
                try:
                    name = stock.get_market_ticker_name(t)
                    df = stock.get_market_ohlcv_by_date(today_str, today_str, t)
                    change = df['등락률'].iloc[0] if not df.empty else 0
                    stocks_info.append({"name": name, "change": float(change)})
                except: continue
            tracking_data[sid] = stocks_info

        analysis = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "market_mood": context.get("market_mood", "Normal"),
            "breadth": breadth_stats,
            "flow_timeline": flow_timeline,
            "stages": {}
        }

        for sid, info in stages_config.items():
            analysis["stages"][sid] = {
                "name": info["name"], "desc": info["desc"], "basis": info["basis"],
                "color": self.get_stage_color(sid),
                "active": sid in signals or (sum([s['change'] for s in tracking_data.get(sid, [])]) / len(tracking_data.get(sid, [])) > 2.0 if tracking_data.get(sid) else False),
                "signals": signals.get(sid, []),
                "tracking_stocks": tracking_data.get(sid, []),
                "is_current": False # 기본값
            }

        # [NEW] 현재 에너지 피크 단계 판정 (등락률 기준)
        max_avg = -999
        current_focus = None
        for sid, stocks in tracking_data.items():
            if not stocks: continue
            avg = sum([s['change'] for s in stocks]) / len(stocks)
            if avg > max_avg:
                max_avg = avg
                current_focus = sid
        
        if current_focus:
            analysis["stages"][current_focus]["is_current"] = True
            analysis["current_stage_name"] = analysis["stages"][current_focus]["name"]

        # [NEW] 에너지 모멘텀(추세) 분석
        if len(flow_timeline) >= 2:
            today_vals = flow_timeline[-1]["values"]
            yesterday_vals = flow_timeline[-2]["values"]
            
            for sid in analysis["stages"]:
                t_val = today_vals.get(sid, 0)
                y_val = yesterday_vals.get(sid, 0)
                
                # 15일 내 최고치 여부 (PEAK 판정)
                all_vals = [day["values"].get(sid, 0) for day in flow_timeline]
                is_peak = (t_val == max(all_vals)) and t_val > 2.0
                
                if is_peak:
                    analysis["stages"][sid]["trend"] = "PEAK"
                elif t_val > y_val:
                    analysis["stages"][sid]["trend"] = "RISING"
                elif t_val < y_val:
                    analysis["stages"][sid]["trend"] = "FALLING"
                else:
                    analysis["stages"][sid]["trend"] = "STABLE"

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"✅ 순환매 레이더 업데이트 완료")

if __name__ == "__main__":
    RotationRadar().run()
