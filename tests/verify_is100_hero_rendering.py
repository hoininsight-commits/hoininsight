import unittest
from pathlib import Path
import re

class TestIS100HeroRendering(unittest.TestCase):
    def test_no_direct_undefined_access(self):
        """
        Verify that render.js does not directly inject potentially undefined properties
        from heroSummary or briefing into the innerHTML of the hero section.
        """
        render_path = Path("docs/ui/render.js")
        if not render_path.exists():
            self.fail("docs/ui/render.js not found")
        
        content = render_path.read_text(encoding='utf-8')
        
        # Check for fallback assignment
        self.assertIn("heroTitle = heroTitle ||", content)
        self.assertIn("heroOneLiner = heroOneLiner ||", content)
        
        # Check that the hero section innerHTML uses the sanitized heroTitle/heroOneLiner
        # and NOT direct heroSummary.headline inside the template literal.
        issue_hook_render = re.search(r"document\.getElementById\('issue-hook'\)\.innerHTML\s*=\s*`([\s\S]+?)`", content)
        self.assertTrue(issue_hook_render, "Could not find issue-hook innerHTML assignment")
        
        inner_html = issue_hook_render.group(1)
        self.assertIn("${heroTitle}", inner_html)
        self.assertIn("${heroOneLiner}", inner_html)
        self.assertNotIn("${heroSummary.headline}", inner_html)
        self.assertNotIn("${heroSummary.one_liner}", inner_html)

    def test_diagnostic_logs_present(self):
        """Verify that console diagnostics for IS-100 are present."""
        render_path = Path("docs/ui/render.js")
        content = render_path.read_text(encoding='utf-8')
        self.assertIn("console.log('[IS-100] Data Diagnostics:'", content)

if __name__ == "__main__":
    unittest.main()
