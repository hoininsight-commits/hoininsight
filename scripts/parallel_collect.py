#!/usr/bin/env python3
"""
멀티 에이전트 병렬 수집 오케스트레이터

각 서브수집기를 독립 subprocess로 실행해 프로세스 격리 + 병렬성 확보.
Phase 1 (독립 에이전트 7개) → Phase 2 (종속 에이전트 2개)

사용법:
    python scripts/parallel_collect.py
    python scripts/parallel_collect.py --phase 1   # Phase 1만
    python scripts/parallel_collect.py --phase 2   # Phase 2만
"""
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PYTHON = sys.executable

PHASE1_AGENTS = [
    ("MARKET",    [PYTHON, "-m", "src.agents.collector.market_agent"]),
    ("MACRO",     [PYTHON, "-m", "src.agents.collector.macro_agent"]),
    ("SENTIMENT", [PYTHON, "-m", "src.agents.collector.sentiment_agent"]),
    ("DART",      [PYTHON, "-m", "src.agents.collector.dart_agent"]),
    ("CONSENSUS", [PYTHON, "-m", "src.agents.collector.financial_collectors", "consensus"]),
    ("COT",       [PYTHON, "-m", "src.agents.collector.financial_collectors", "cot"]),
    ("PUTCALL",   [PYTHON, "-m", "src.agents.collector.putcall_collector"]),
]

PHASE2_AGENTS = [
    ("FLOW",   [PYTHON, "-m", "src.agents.collector.flow_collector"]),
    ("SOCIAL", [PYTHON, "-m", "src.agents.collector.social_agent"]),
]


def run_agents_parallel(agents: list) -> dict:
    procs = {}
    for name, cmd in agents:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=PROJECT_ROOT,
        )
        procs[name] = proc
        print(f"  ▶ [{name}] 시작 (PID {proc.pid})")

    results = {}
    for name, proc in procs.items():
        stdout, _ = proc.communicate()
        ok = proc.returncode == 0
        results[name] = {"success": ok, "returncode": proc.returncode}
        icon = "✅" if ok else "❌"
        print(f"  {icon} [{name}] 완료 (exit {proc.returncode})")
        if not ok:
            for line in stdout.splitlines()[-5:]:
                print(f"     {line}")
    return results


def main():
    phase_arg = None
    if "--phase" in sys.argv:
        idx = sys.argv.index("--phase")
        phase_arg = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else None

    print(f"\n🚀 멀티 에이전트 병렬 수집 [{datetime.now().strftime('%Y%m%d %H:%M:%S')}]")
    t0 = time.time()
    all_results = {}

    if phase_arg != 2:
        print(f"\n  [Phase 1] 독립 에이전트 {len(PHASE1_AGENTS)}개 병렬 실행...")
        all_results.update(run_agents_parallel(PHASE1_AGENTS))

    if phase_arg != 1:
        print(f"\n  [Phase 2] 종속 에이전트 {len(PHASE2_AGENTS)}개 병렬 실행...")
        all_results.update(run_agents_parallel(PHASE2_AGENTS))

    success = sum(1 for r in all_results.values() if r["success"])
    total = len(all_results)
    elapsed = time.time() - t0
    print(f"\n✅ 완료 — {elapsed:.1f}초 (성공: {success}/{total})")
    return 0 if success == total else 1


if __name__ == "__main__":
    sys.exit(main())
