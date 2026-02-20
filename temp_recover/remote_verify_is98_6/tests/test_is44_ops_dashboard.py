import unittest
from pathlib import Path
from src.reporters.decision_dashboard import DecisionDashboard, DecisionCard

class TestIS44OperationalDashboard(unittest.TestCase):
    def setUp(self):
        self.dashboard = DecisionDashboard(Path("."))
        self.mock_card = DecisionCard(
            topic_id="test_id",
            title="테스트 토픽 제목",
            status="READY",
            reason="테스트 이유",
            output_format_ko="대형 영상",
            editorial_reason_ko="지금 발화해야 함",
            why_today="오늘의 이유",
            tags=["TICKER"],
            is_fact_driven=True,
            content_package={"type": "대형 영상", "content": "스크립트 내용"}
        )

    def test_localization_korean_only(self):
        data = {"cards": [self.mock_card]}
        md = self.dashboard.render_operational_view(data, "2026-01-30")
        
        # Check for Korean labels
        self.assertIn("회의 보드", md)
        self.assertIn("발화 확정", md)
        self.assertIn("판단 요약", md)
        
        # Check that English technical status is not in the plain text labels (outside code/links)
        self.assertNotIn("BOARD", md)
        self.assertNotIn("DETAIL", md)
        self.assertNotIn("`READY`", md)
        self.assertNotIn("`HOLD`", md)
        self.assertNotIn("`SILENT`", md)

    def test_five_sections_presence(self):
        data = {"cards": [self.mock_card]}
        md = self.dashboard.render_operational_view(data, "2026-01-30")
        
        self.assertIn("① 토픽 요약", md)
        self.assertIn("② 판단 근거 요약", md)
        self.assertIn("③ 자본 경로 및 종목", md)
        self.assertIn("④ 콘텐츠 패키지", md)
        self.assertIn("⑤ 사후 판단 참고", md)

if __name__ == '__main__':
    unittest.main()
