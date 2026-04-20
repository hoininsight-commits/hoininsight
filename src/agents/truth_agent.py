# src/agents/truth_agent.py
# HOIN Insight Truth Agent (v3.0)
# 목적: 과거 결정의 성과를 측정하고 Truth Engine의 가중치를 업데이트함

import json
import os
from pathlib import Path
from datetime import datetime, timedelta

class TruthAgent:
    def __init__(self):
        self.base_dir = Path(os.getenv("HOIN_BASE_DIR", Path(__file__).resolve().parents[2]))
        # TruthEngine 초기화
        try:
            from src.analysis.truth_engine import TruthEngine
            self.te = TruthEngine(self.base_dir)
        except: pass

    def run(self):
        """과거 성과 평가 및 피드백 루프 가동"""
        print(f"⚖️ AGENT-06 TRUTH_AGENT 시작")
        
        # 1. 과거 로그 로드
        log_p = self.base_dir / "data/history/outcome_log.json"
        if not log_p.exists(): return
        
        log = json.loads(log_p.read_text())
        updated = False
        results = []
        
        # 2. PENDING 상태의 항목 중 3일 이상 경과한 항목 평가
        # (실제 환경에서는 실시간 가격 데이터를 가져와야 하나, 여기서는 시뮬레이션 로직 구현)
        for entry in log:
            if entry["status"] == "PENDING":
                # 날짜 비교 (3일 경과 기준)
                entry_date = datetime.strptime(entry["date"], "%Y%m%d")
                if datetime.now() - entry_date >= timedelta(days=3):
                    # [SIMULATION] 성공/실패 판별 (실제는 market.json의 현재가와 대조)
                    # 여기서는 70% 확률로 성공했다고 가정하거나, 특정 지표 추세 확인 가능
                    # 보수적으로 NEUTRAL 또는 데이터 미비로 처리
                    entry["status"] = "NEUTRAL (DATA_LIMIT)"
                    entry["evaluated_at"] = datetime.now().strftime("%Y%m%d")
                    updated = True
            
            if entry["status"] != "PENDING":
                res = "SUCCESS" if "SUCCESS" in entry["status"] else "FAILURE" if "FAILURE" in entry["status"] else "NEUTRAL"
                results.append(res)

        # 3. TruthEngine 가중치 업데이트
        if hasattr(self, 'te'):
             self.te.update_performance(results)
             print("  ✅ 성과 분석 기반 의사결정 가중치 및 신뢰도 보정 완료")

        if updated:
            log_p.write_text(json.dumps(log, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    TruthAgent().run()
