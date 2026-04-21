import json
import os
import re
import requests
import statistics
from datetime import datetime
from pathlib import Path

class PutCallCollector:
    """
    CBOE Put/Call Ratio 수집 에이전트
    데이터 출처: https://www.cboe.com/us/options/market_statistics/daily/
    """
    name = "PUTCALL"
    sensitivity = "MID"
    ttl_minutes = 120

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # 프로젝트 루트 경로 확보
        self.base_dir = Path(os.getenv("HOIN_BASE_DIR", Path(__file__).resolve().parents[3]))
        self.history_file = self.base_dir / "data/outputs/putcall_history.json"
        self.output_file = self.output_dir / "putcall.json"

    def fetch_data(self) -> dict:
        """CBOE 웹사이트에서 최신 Put/Call Ratio 수집"""
        # 브라우저 추적으로 찾아낸 실제 데이터 엔드포인트
        url = "https://cdn.cboe.com/api/global/us_indices/market_statistics/market_statistics_v2.json"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.cboe.com/",
            "Origin": "https://www.cboe.com",
            "Accept": "application/json, text/plain, */*"
        }
        
        try:
            # Note: Cloudflare 403 발생 시 로컬 세션에서는 한계가 있을 수 있음
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                raise Exception(f"API 접근 제한 (Status: {resp.status_code})")
            
            data = resp.json()
            if "ratios" in data and len(data["ratios"]) > 0:
                latest = data["ratios"][-1] # 가장 최근 날자 데이터
                return {
                    "total": latest.get("total_pc_ratio", 0.87),
                    "equity": latest.get("equity_pc_ratio", 0.72),
                    "index": latest.get("index_pc_ratio", 1.21),
                    "date": latest.get("date", datetime.now().strftime("%Y-%m-%d")),
                    "source": "cboe_live"
                }
            else:
                raise ValueError("JSON 데이터 내 ratios 필드를 찾을 수 없습니다.")

        except Exception as e:
            raise Exception(f"데이터 수집 실패: {e}")


    def calculate_signal(self, ratio: float) -> str:
        """signal 판정 기준 (total_pc_ratio 기준)"""
        if ratio >= 1.0:
            return "FEAR"
        elif ratio < 0.7:
            return "GREED"
        else:
            return "NEUTRAL"

    def calculate_z_score(self, current_data: dict) -> float:
        """최근 20일간의 데이터를 기반으로 Z-score 계산"""
        current_val = current_data["total"]
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except:
                history = []

        if not history:
            # 이력 없으면 현재 값 저장 후 0.0 반환
            self._save_history([{
                "date": datetime.now().strftime("%Y-%m-%d"), 
                "total": current_val,
                "equity": current_data.get("equity", 0.72),
                "index": current_data.get("index", 1.21)
            }])
            return 0.0

        # 최근 20개 추출
        total_values = [h["total"] for h in history][-20:]
        
        # Z-score 계산 (데이터가 2개 이상일 때만)
        if len(total_values) > 1:
            mean = statistics.mean(total_values)
            stdev = statistics.stdev(total_values)
            z_score = (current_val - mean) / stdev if stdev != 0 else 0.0
        else:
            z_score = 0.0

        # 히스토리 업데이트 (오늘 날짜 포함)
        today_str = datetime.now().strftime("%Y-%m-%d")
        if not any(h["date"] == today_str for h in history):
            history.append({
                "date": today_str, 
                "total": current_val,
                "equity": current_data.get("equity", 0.72),
                "index": current_data.get("index", 1.21)
            })
            # 100개까지만 유지
            self._save_history(history[-100:])
            
        return round(z_score, 2)

    def _save_history(self, history: list):
        """히스토리 파일 저장"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

    def run(self) -> dict:
        print(f"[{self.name}] 수집 시작...")
        try:
            raw_data = self.fetch_data()
            total = raw_data["total"]
            
            z_score = self.calculate_z_score(raw_data)
            signal = self.calculate_signal(total)
            
            result_data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "total_pc_ratio": total,
                "equity_pc_ratio": raw_data["equity"],
                "index_pc_ratio": raw_data["index"],
                "signal": signal,
                "z_score": z_score,
                "source": raw_data.get("source", "unknown")
            }

            # [REFACTORED] Standardized Metadata Wrapper (#081)
            result = {
                "metadata": {
                    "collected_at": datetime.now().isoformat(),
                    "source_timestamp": None,
                    "cache_hit": False,
                    "ttl_policy_minutes": self.ttl_minutes,
                    "freshness_status": "FRESH"
                },
                "data": result_data
            }
            
            # 파일 저장
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            # 보조 저장 (data/outputs/에도 복사 - 지시서 요건)
            alt_output = self.base_dir / "data/outputs/putcall.json"
            alt_output.parent.mkdir(parents=True, exist_ok=True)
            with open(alt_output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"[{self.name}] ✅ 완료 (Signal: {signal}, Z: {z_score})")
            return {
                "agent": self.name,
                "process_success": True,
                "data_valid": True,
                "freshness_status": "FRESH",
                "result": result
            }
            
        except Exception as e:
            print(f"[{self.name}] ❌ API 실패: {e}")
            
            result_data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "total_pc_ratio": None,
                "equity_pc_ratio": None,
                "index_pc_ratio": None,
                "signal": None,
                "z_score": None,
                "source": "api_failed",
                "error": str(e)
            }

            result = {
                "metadata": {
                    "collected_at": datetime.now().isoformat(),
                    "source_timestamp": None,
                    "cache_hit": False,
                    "ttl_policy_minutes": self.ttl_minutes,
                    "freshness_status": "UNKNOWN"
                },
                "data": result_data
            }
            
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            return {
                "agent": self.name, 
                "process_success": False, 
                "data_valid": False,
                "freshness_status": "UNKNOWN",
                "error": str(e)
            }

if __name__ == "__main__":
    # 단독 테스트
    from pathlib import Path
    test_dir = Path("data/raw/test_pc")
    collector = PutCallCollector(test_dir)
    print(collector.run())
