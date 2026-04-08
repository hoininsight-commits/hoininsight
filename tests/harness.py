# tests/harness.py
# HOIN Insight 전체 파이프라인 하네스
# 실제 API 없이 가짜 데이터로 전체 흐름을 테스트한다

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 경로에 추가
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

FIXTURES = Path(__file__).parent / "fixtures"
TODAY = datetime.now().strftime("%Y%m%d")
TEST_DATE = "20260408"  # 하네스는 고정 날짜 사용


def setup_test_environment():
    """테스트용 data/ 폴더에 가짜 데이터 주입"""
    print("  테스트 환경 설정 중...")

    raw_dir = ROOT / "data" / "raw" / TEST_DATE
    raw_dir.mkdir(parents=True, exist_ok=True)

    # 가짜 데이터 복사
    shutil.copy(FIXTURES / "mock_market.json", raw_dir / "market.json")
    shutil.copy(FIXTURES / "mock_macro.json", raw_dir / "macro.json")
    shutil.copy(FIXTURES / "mock_sentiment.json", raw_dir / "sentiment.json")

    print(f"  가짜 데이터 주입 완료: data/raw/{TEST_DATE}/")


def test_detector_with_mock_data():
    """AGENT-03: 가짜 데이터로 신호 감지 테스트"""
    print("\n[AGENT-03 DETECTOR 하네스 테스트]")

    import src.agents.detector as detector_module

    try:
        agent = detector_module.DetectorAgent.__new__(detector_module.DetectorAgent)
        agent.today = TEST_DATE
        agent.raw_dir = ROOT / "data" / "raw" / TEST_DATE
        agent.signal_dir = ROOT / "data" / "signals" / TEST_DATE
        agent.signal_dir.mkdir(parents=True, exist_ok=True)
        agent.history_path = ROOT / "data" / "history" / "signal_log.json"
        agent.history_path.parent.mkdir(parents=True, exist_ok=True)

        from src.core.filters import SignalFilters
        agent.filters = SignalFilters()

        # 데이터 로드 및 후보 생성
        raw_data = agent.load_raw_data()
        assert raw_data, "Raw 데이터 로드 실패"

        candidates = agent.build_candidates(raw_data)
        assert len(candidates) > 0, "후보 신호 없음"

        print(f"  후보 신호: {len(candidates)}개")

        selected = agent.select_topic(candidates)
        assert selected is not None, "신호 선정 실패"

        print(f"  선정 토픽: {selected['topic']}")
        print(f"  신호 강도: {selected['strength']}")

        agent.save_results(candidates, selected)

        # 출력 파일 검증
        candidates_path = agent.signal_dir / "candidates.json"
        assert candidates_path.exists(), "candidates.json 생성 실패"

        candidates_data = json.loads(candidates_path.read_text())
        assert "candidates" in candidates_data
        assert "total_candidates" in candidates_data

        print("  candidates.json 생성 확인")

        if selected.get("selected"):
            signal_path = agent.signal_dir / "today_signal.json"
            assert signal_path.exists(), "today_signal.json 생성 실패"

            signal_data = json.loads(signal_path.read_text())
            required_fields = ["date", "topic", "strength", "content_type", "filters_hit"]
            for field in required_fields:
                assert field in signal_data, f"필수 필드 누락: {field}"

            print("  today_signal.json 생성 및 스키마 확인")
            return True, selected

        return True, None

    except Exception as e:
        print(f"  FAIL: {e}")
        return False, None


def test_history_update():
    """이력 파일 업데이트 검증"""
    print("\n[이력 파일 하네스 테스트]")

    history_path = ROOT / "data" / "history" / "signal_log.json"
    content_log_path = ROOT / "data" / "history" / "content_log.json"

    # signal_log.json 존재 확인
    assert history_path.exists(), "signal_log.json 없음"
    data = json.loads(history_path.read_text())
    assert "signals" in data
    print(f"  signal_log.json 확인 (누적 신호: {len(data['signals'])}개)")

    # content_log.json 존재 확인
    assert content_log_path.exists(), "content_log.json 없음"
    data = json.loads(content_log_path.read_text())
    assert "contents" in data
    print(f"  content_log.json 확인 (누적 콘텐츠: {len(data['contents'])}개)")

    return True


def test_writer_output():
    """AGENT-05: 스크립트 파일 생성 확인"""
    print("\n[AGENT-05 WRITER 하네스 테스트]")

    scripts_dir = ROOT / "data" / "scripts"
    if not scripts_dir.exists():
        print("  scripts/ 폴더 없음 — 건너뜀")
        return True

    # 가장 최근 스크립트 확인
    script_dirs = sorted(scripts_dir.iterdir(), reverse=True)
    if not script_dirs:
        print("  생성된 스크립트 없음 — 건너뜀")
        return True

    latest = script_dirs[0]
    long_path = latest / "today_script_long.md"
    short_path = latest / "today_script_short.md"

    if long_path.exists():
        content = long_path.read_text(encoding="utf-8")
        assert len(content) > 500, "롱폼 스크립트가 너무 짧음"
        print(f"  롱폼 스크립트 확인 ({len(content)}자)")
    else:
        print("  롱폼 스크립트 없음 — 건너뜀")

    if short_path.exists():
        content = short_path.read_text(encoding="utf-8")
        assert len(content) > 100, "쇼츠 스크립트가 너무 짧음"
        print(f"  쇼츠 스크립트 확인 ({len(content)}자)")
    else:
        print("  쇼츠 스크립트 없음 — 건너뜀")

    return True


def test_publisher_output():
    """AGENT-06: 이력 및 대시보드 파일 확인"""
    print("\n[AGENT-06 PUBLISHER 하네스 테스트]")

    content_log = ROOT / "data" / "history" / "content_log.json"
    dashboard_data = ROOT / "dashboard" / "today_data.json"

    assert content_log.exists(), "content_log.json 없음"
    data = json.loads(content_log.read_text())
    assert "contents" in data
    print(f"  content_log.json 확인 (항목: {len(data['contents'])}개)")

    if dashboard_data.exists():
        data = json.loads(dashboard_data.read_text())
        assert "today" in data
        assert "last_updated" in data
        print("  dashboard/today_data.json 확인")
    else:
        print("  dashboard/today_data.json 없음 — 건너뜀")

    return True


def run_harness():
    """전체 하네스 실행"""
    print("=" * 50)
    print("HOIN Insight 파이프라인 하네스 시작")
    print(f"테스트 날짜: {TEST_DATE}")
    print("=" * 50)

    results = {}

    # 환경 설정
    setup_test_environment()

    # AGENT-03 테스트
    ok, signal = test_detector_with_mock_data()
    results["detector"] = ok

    # 이력 파일 테스트
    try:
        ok = test_history_update()
        results["history"] = ok
    except Exception as e:
        print(f"  이력 파일 테스트 실패: {e}")
        results["history"] = False

    # AGENT-05 테스트
    try:
        ok = test_writer_output()
        results["writer"] = ok
    except Exception as e:
        print(f"  WRITER 테스트 실패: {e}")
        results["writer"] = False

    # AGENT-06 테스트
    try:
        ok = test_publisher_output()
        results["publisher"] = ok
    except Exception as e:
        print(f"  PUBLISHER 테스트 실패: {e}")
        results["publisher"] = False

    # 결과 요약
    print("\n" + "=" * 50)
    print("하네스 결과 요약")
    print("=" * 50)

    all_passed = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n전체 하네스 PASS")
        return 0
    else:
        print("\n일부 하네스 FAIL — 위 결과 확인")
        return 1


if __name__ == "__main__":
    sys.exit(run_harness())
