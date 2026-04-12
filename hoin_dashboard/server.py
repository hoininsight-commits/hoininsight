"""
HOIN Insight 로컬 운영자 대시보드 서버
Python 표준 라이브러리만 사용 (외부 패키지 없음)
실행: python3 hoin_dashboard/server.py
접속: http://localhost:8888
"""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 (hoin_dashboard/ 의 상위 디렉토리)
ROOT = Path(__file__).parent.parent
PORT = int(os.environ.get("PORT", 8888))


def _latest_date_dir(base: Path):
    if not base.exists():
        return None
    dirs = sorted([d for d in base.iterdir() if d.is_dir() and d.name.isdigit()], reverse=True)
    return dirs[0] if dirs else None


def api_market():
    raw_dir = _latest_date_dir(ROOT / "data" / "raw")
    if not raw_dir:
        return {"error": "데이터 없음", "date": None}
    market_file = raw_dir / "market.json"
    if not market_file.exists():
        return {"error": "market.json 없음", "date": raw_dir.name}
    data = json.loads(market_file.read_text())
    return {"date": raw_dir.name, **data}


def api_signal():
    sig_dir = _latest_date_dir(ROOT / "data" / "signals")
    if not sig_dir:
        return {"error": "신호 없음", "date": None}
    signal_file = sig_dir / "today_signal.json"
    if not signal_file.exists():
        return {"error": "today_signal.json 없음", "date": sig_dir.name}
    return json.loads(signal_file.read_text())


def api_agents():
    today = datetime.now().strftime("%Y%m%d")
    agents = [
        ("AGENT-01 COLLECTOR",  ROOT / "data" / "raw" / today / "market.json"),
        ("AGENT-02 LEARNER",    ROOT / "data" / "learning"),
        ("AGENT-03 DETECTOR",   ROOT / "data" / "signals" / today / "today_signal.json"),
        ("AGENT-04 ANALYST",    ROOT / "data" / "analysis" / today),
        ("AGENT-05 WRITER",     ROOT / "data" / "scripts" / today),
        ("AGENT-06 PUBLISHER",  ROOT / "dashboard" / "today_data.json"),
    ]
    result = []
    for name, path in agents:
        ok = Path(path).exists()
        result.append({"name": name, "ok": ok, "status": "완료" if ok else "대기"})
    return {"date": today, "agents": result}


def api_filters():
    sig_dir = _latest_date_dir(ROOT / "data" / "signals")
    if not sig_dir:
        return {"error": "신호 없음"}
    candidates_file = sig_dir / "candidates.json"
    if not candidates_file.exists():
        return {"error": "candidates.json 없음", "date": sig_dir.name}
    return {"date": sig_dir.name, "candidates": json.loads(candidates_file.read_text())}


def api_history():
    log_file = ROOT / "data" / "history" / "signal_log.json"
    if not log_file.exists():
        return {"error": "signal_log.json 없음", "entries": []}
    data = json.loads(log_file.read_text())
    # 최신 20개만
    entries = data if isinstance(data, list) else data.get("signals", [])
    return {"count": len(entries), "entries": entries[-20:]}


def api_harness():
    items = []

    def chk(name, ok, detail=""):
        items.append({"name": name, "ok": ok, "detail": detail})

    # 1. 최신 시장 데이터
    raw_dir = _latest_date_dir(ROOT / "data" / "raw")
    chk("시장 데이터 수집", raw_dir is not None,
        raw_dir.name if raw_dir else "data/raw/ 없음")

    # 2. 신호 감지
    sig_dir = _latest_date_dir(ROOT / "data" / "signals")
    chk("신호 감지", sig_dir is not None,
        sig_dir.name if sig_dir else "data/signals/ 없음")

    # 3. today_signal.json 존재
    if sig_dir:
        sf = sig_dir / "today_signal.json"
        chk("today_signal.json", sf.exists(),
            f"{sig_dir.name}/today_signal.json")
    else:
        chk("today_signal.json", False, "신호 디렉토리 없음")

    # 4. dashboard/today_data.json
    dash = ROOT / "dashboard" / "today_data.json"
    chk("대시보드 데이터", dash.exists(), str(dash.relative_to(ROOT)))

    # 5. docs/index.html
    docs = ROOT / "docs" / "index.html"
    chk("GitHub Pages index.html", docs.exists(), str(docs.relative_to(ROOT)))

    # 6. signal_log.json
    log = ROOT / "data" / "history" / "signal_log.json"
    chk("신호 이력", log.exists(), str(log.relative_to(ROOT)))

    # 7. GEMINI_API_KEY (환경변수)
    gemini = bool(os.environ.get("GEMINI_API_KEY", ""))
    chk("GEMINI_API_KEY", gemini, "환경변수 설정됨" if gemini else ".env 미설정")

    # 8. 오늘 분석 데이터
    today = datetime.now().strftime("%Y%m%d")
    analysis = ROOT / "data" / "analysis" / today
    chk("AGENT-04 분석 데이터", analysis.exists(),
        f"data/analysis/{today}" if analysis.exists() else "오늘 분석 없음")

    # 9. 오늘 스크립트
    scripts = ROOT / "data" / "scripts" / today
    chk("AGENT-05 스크립트", scripts.exists(),
        f"data/scripts/{today}" if scripts.exists() else "오늘 스크립트 없음")

    ok_count = sum(1 for i in items if i["ok"])
    total = len(items)
    score = round(ok_count / total * 100)
    grade = "S" if score >= 90 else "A" if score >= 70 else "B" if score >= 50 else "C"

    return {"score": score, "grade": grade, "ok": ok_count, "total": total, "items": items}


ROUTES = {
    "/api/harness": api_harness,
    "/api/market":  api_market,
    "/api/signal":  api_signal,
    "/api/agents":  api_agents,
    "/api/filters": api_filters,
    "/api/history": api_history,
}

INDEX_HTML = Path(__file__).parent / "index.html"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # 로그 억제

    def do_GET(self):
        path = self.path.split("?")[0]

        if path in ROUTES:
            try:
                data = ROUTES[path]()
                body = json.dumps(data, ensure_ascii=False, indent=2).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({"error": str(e)}, ensure_ascii=False).encode()
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(body)

        elif path == "/" or path == "/index.html":
            if INDEX_HTML.exists():
                body = INDEX_HTML.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    os.chdir(ROOT)
    server = HTTPServer(("localhost", PORT), Handler)
    print(f"HOIN 대시보드 서버 시작: http://localhost:{PORT}")
    print("종료: Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n서버 종료")
