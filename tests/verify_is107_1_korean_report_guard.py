import unittest
import re
from pathlib import Path

class TestIS107_1KoreanReportGuard(unittest.TestCase):
    def setUp(self):
        self.engine_docs_dir = Path("docs/engine")

    def test_reports_contain_korean(self):
        # Scan all IS-*_REMOTE_VERIFICATION_REPORT.md files
        reports = list(self.engine_docs_dir.glob("IS-*_REMOTE_VERIFICATION_REPORT.md"))
        self.assertTrue(len(reports) > 0, "No verification reports found")

        for report_path in reports:
            content = report_path.read_text(encoding='utf-8')
            # Check for Hangul in the first 500 chars (sufficient for header/intro)
            has_korean = any('\u1100' <= char <= '\u11ff' or 
                             '\u3130' <= char <= '\u318f' or 
                             '\uac00' <= char <= '\ud7af' for char in content[:500])
            
            # Since some older reports might be English, we only enforce this strictly 
            # for the newly created IS-107-1 report or any report updated from now.
            if "IS-107-1" in report_path.name:
                self.assertTrue(has_korean, f"Report {report_path.name} must contain Korean characters")
                self.assertIn("✅ PASS", content, f"Report {report_path.name} must include '✅ PASS'")
                self.assertIn("커밋 해시", content, f"Report {report_path.name} must include '커밋 해시'")
                
                has_file_header = any(keyword in content for keyword in ["추가된 파일", "변경된 파일", "산출물"])
                self.assertTrue(has_file_header, f"Report {report_path.name} must include file/output headers")

    def test_template_exists(self):
        template = Path("docs/engine/templates/REMOTE_VERIFICATION_REPORT_KO_TEMPLATE.md")
        self.assertTrue(template.exists())

if __name__ == "__main__":
    unittest.main()
