# src/agents/publisher.py
# AGENT-06 PUBLISHER
# 역할: 이력 저장 + 대시보드 업데이트 + 선장 브리핑

import json
from datetime import datetime
from pathlib import Path


class PublisherAgent:

    def __init__(self):
        import os
        self.base_dir = Path(os.getenv("HOIN_BASE_DIR", Path(__file__).resolve().parents[2]))
        self.today = datetime.now().strftime("%Y%m%d")
        self.content_log_path = Path("data/history/content_log.json")
        self.signal_log_path = Path("data/history/signal_log.json")
        self.dashboard_dir = Path("dashboard")
        self.dashboard_dir.mkdir(exist_ok=True)

    def load_today_data(self) -> dict:
        """오늘 생성된 모든 데이터 로드"""
        data = {}

        # 신호
        for d in sorted(Path("data/signals").iterdir(), reverse=True):
            p = d / "today_signal.json"
            if p.exists():
                data["signal"] = json.loads(p.read_text())
                break

        # 분석
        if Path("data/analysis").exists():
            for d in sorted(Path("data/analysis").iterdir(), reverse=True):
                p = d / "today_analysis.json"
                if p.exists():
                    data["analysis"] = json.loads(p.read_text())
                    break

        # 종목
        if Path("data/analysis").exists():
            for d in sorted(Path("data/analysis").iterdir(), reverse=True):
                p = d / "today_stocks.json"
                if p.exists():
                    data["stocks"] = json.loads(p.read_text())
                    break

        # 스크립트
        if Path("data/scripts").exists():
            for d in sorted(Path("data/scripts").iterdir(), reverse=True):
                p = d / "today_script_long.md"
                if p.exists():
                    data["script_long_path"] = str(p)
                    break

            for d in sorted(Path("data/scripts").iterdir(), reverse=True):
                p = d / "today_script_short.md"
                if p.exists():
                    data["script_short_path"] = str(p)
                    break

        # 후보 목록
        for d in sorted(Path("data/signals").iterdir(), reverse=True):
            p = d / "candidates.json"
            if p.exists():
                data["candidates"] = json.loads(p.read_text())
                break

        # market 데이터 (대시보드 A구역용)
        if Path("data/raw").exists():
            for d in sorted(Path("data/raw").iterdir(), reverse=True):
                p = d / "market.json"
                if p.exists():
                    data["market"] = json.loads(p.read_text())
                    break

        # macro 데이터
        if Path("data/raw").exists():
            for d in sorted(Path("data/raw").iterdir(), reverse=True):
                p = d / "macro.json"
                if p.exists():
                    data["macro"] = json.loads(p.read_text())
                    break

        # sentiment 데이터
        if Path("data/raw").exists():
            for d in sorted(Path("data/raw").iterdir(), reverse=True):
                p = d / "sentiment.json"
                if p.exists():
                    data["sentiment"] = json.loads(p.read_text())
                    break

        # putcall 데이터
        p = Path("data/outputs/putcall.json")
        if p.exists():
            data["putcall"] = json.loads(p.read_text())

        return data

    def update_content_log(self, data: dict) -> dict:
        """content_log.json에 오늘 콘텐츠 추가"""
        signal = data.get("signal", {})
        if not signal:
            print("  신호 없음 — 이력 업데이트 건너뜀")
            return {}

        stocks = data.get("stocks", {})
        stock_names = [
            s["name"] for s in stocks.get("stocks", [])[:3]
        ]

        # 새 콘텐츠 항목
        new_content = {
            "id": f"{self.today}_001",
            "date": f"{self.today[:4]}-{self.today[4:6]}-{self.today[6:]}",
            "type": signal.get("content_type", "롱폼"),
            "title": signal.get("topic", ""),
            "thumbnail_text": "",
            "duration_min": 15 if signal.get("content_type") == "롱폼" else 2,
            "signal_strength": signal.get("strength", 0),
            "filters_used": signal.get("filters_hit", []),
            "stocks": stock_names,
            "is_republish": signal.get("is_republish", False),
            "original_id": None,
            "script_path": data.get("script_long_path", ""),
            "status": "승인대기",
            "operator_approved": False,
            "approved_at": None,
        }

        # 기존 이력 로드
        log = {"contents": []}
        if self.content_log_path.exists():
            try:
                log = json.loads(self.content_log_path.read_text())
            except Exception:
                pass

        # 오늘 날짜 이미 있으면 업데이트, 없으면 추가
        existing_ids = [c["id"] for c in log["contents"]]
        if new_content["id"] not in existing_ids:
            log["contents"].append(new_content)
        else:
            log["contents"] = [
                new_content if c["id"] == new_content["id"] else c
                for c in log["contents"]
            ]

        self.content_log_path.write_text(
            json.dumps(log, ensure_ascii=False, indent=2)
        )
        print(f"  content_log.json 업데이트 (누적: {len(log['contents'])}개)")
        return new_content

    def update_signal_log(self, data: dict):
        """signal_log.json 업데이트 (탈락 후보 포함)"""
        candidates = data.get("candidates", {})
        signal = data.get("signal", {})

        log = {"signals": []}
        if self.signal_log_path.exists():
            try:
                log = json.loads(self.signal_log_path.read_text())
            except Exception:
                pass

        # 오늘 날짜 이미 있으면 스킵
        today_str = f"{self.today[:4]}-{self.today[4:6]}-{self.today[6:]}"
        existing_dates = [s.get("date") for s in log["signals"]]
        if today_str in existing_dates:
            print("  signal_log.json 이미 오늘 날짜 존재 — 스킵")
            return

        log["signals"].append({
            "date": today_str,
            "topic": signal.get("topic", "없음"),
            "strength": signal.get("strength", 0),
            "selected": True if signal else False,
            "content_type": signal.get("content_type", ""),
            "total_candidates": candidates.get("total_candidates", 0),
        })

        self.signal_log_path.write_text(
            json.dumps(log, ensure_ascii=False, indent=2)
        )
        print(f"  signal_log.json 업데이트 (누적: {len(log['signals'])}개)")

    def generate_dashboard_data(self, data: dict, content: dict, pipeline_results: dict = None):
        """대시보드용 JSON 생성"""
        signal = data.get("signal", {})
        analysis = data.get("analysis", {})
        stocks = data.get("stocks", {})
        candidates = data.get("candidates", {})

        market = data.get("market", {})
        macro = data.get("macro", {})
        sentiment = data.get("sentiment", {})
        putcall = data.get("putcall", {})
        
        # 파이프라인 결과에서 fact_checker 상태 추출
        fact_checker = {}
        if pipeline_results and "fact_checker" in pipeline_results:
            fact_checker = pipeline_results["fact_checker"]

        dashboard_data = {
            "last_updated": datetime.now().isoformat(),
            "today": {
                "date": f"{self.today[:4]}-{self.today[4:6]}-{self.today[6:]}",
                "signal": signal,
                "analysis": analysis,
                "stocks": stocks.get("stocks", []),
                "candidates": candidates.get("candidates", []),
                "content_id": content.get("id", ""),
                "status": "승인대기",
                "fact_checker": fact_checker,
                "putcall": putcall
            },
            "market": market,
            "macro": macro,
            "sentiment": sentiment,
            "putcall": putcall # 하위 호환성 및 접근성 위해 최상단에도 추가
        }

        output_path = self.dashboard_dir / "today_data.json"
        output_path.write_text(
            json.dumps(dashboard_data, ensure_ascii=False, indent=2)
        )
        # GitHub Pages용 docs 폴더 업데이트
        docs_path = self.base_dir / "docs" / "today_data.json"
        docs_path.write_text(
            json.dumps(dashboard_data, ensure_ascii=False, indent=2)
        )
        print(f"  대시보드 데이터 생성: {output_path}, {docs_path}")

    def generate_brief(self, data: dict) -> str:
        """선장 확인용 브리핑 텍스트 생성"""
        signal = data.get("signal", {})
        stocks = data.get("stocks", {})
        analysis = data.get("analysis", {})

        stock_list = "\n".join([
            f"  - {s['name']} ({s['sector']}): {s['impact']} — {s['reason']}"
            for s in stocks.get("stocks", [])[:3]
        ])

        # Analyst의 레벨2 체인 우선 순위 적용
        analysis_chain = analysis.get("level2_chain", [])
        signal_chain = signal.get("level2_chain", [])
        final_chain = analysis_chain if analysis_chain else signal_chain

        chain_str = "\n".join([
            f"  {i+1}. {step}"
            for i, step in enumerate(final_chain)
        ])

        brief = f"""
========================================
HOIN Insight 일일 브리핑
날짜: {self.today[:4]}-{self.today[4:6]}-{self.today[6:]}
========================================

[오늘의 신호]
토픽: {signal.get("topic", "없음")}
강도: {signal.get("strength", 0)} / 10
유형: {signal.get("content_type", "")}
적중 필터: {", ".join(signal.get("filters_hit", []))}
긴급도: {signal.get("urgency", "")}

[레벨2 인과관계]
{chain_str if chain_str else ("  분석 실패 (AGENT-04 오류)" if data.get("analyst_failed") else "  없음 (AGENT-04 미실행)")}

[관련 종목]
{stock_list if stock_list else ("  매핑 실패 (AGENT-04 오류)" if data.get("analyst_failed") else "  종목 데이터 없음 (AGENT-04 미실행)")}

[스크립트]
롱폼: {data.get("script_long_path", "미생성")}
쇼츠: {data.get("script_short_path", "미생성")}

[승인 대기 중]
대시보드에서 확인 후 승인해주세요.
========================================
"""
        brief_path = self.dashboard_dir / "today_brief.txt"
        brief_path.write_text(brief, encoding="utf-8")
        print(f"  선장 브리핑 생성: {brief_path}")
        return brief

    def run(self, pipeline_results: dict = None):
        print(f"\n📢 AGENT-06 PUBLISHER 시작 [{self.today}]")

        data = self.load_today_data()

        if not data:
            print("  데이터 없음 — 종료")
            return {}

        # 파이프라인 실시간 결과 반영 (디스크 로딩 보완)
        if pipeline_results:
            if "analyst" in pipeline_results:
                ar = pipeline_results["analyst"]
                if ar.get("analysis"):
                    data["analysis"] = ar["analysis"]
                if ar.get("stocks"):
                    data["stocks"] = ar["stocks"]
                if ar.get("failed"):
                    data["analyst_failed"] = True
                    if "signal" in data:
                        # 신호 객체에도 체인 업데이트 (실패 시 빈 배열 유지)
                        data["signal"]["level2_chain"] = []
                elif ar.get("analysis"):
                    if "signal" in data:
                        data["signal"]["level2_chain"] = ar["analysis"].get("level2_chain", [])

        # 이력 업데이트
        content = self.update_content_log(data)
        self.update_signal_log(data)

        # 대시보드 데이터 생성
        self.generate_dashboard_data(data, content, pipeline_results)

        # 선장 브리핑 생성
        brief = self.generate_brief(data)

        # 브리핑 출력
        print(brief)

        print("✅ AGENT-06 완료\n")
        return {"content": content, "brief": brief}


if __name__ == "__main__":
    agent = PublisherAgent()
    agent.run()
