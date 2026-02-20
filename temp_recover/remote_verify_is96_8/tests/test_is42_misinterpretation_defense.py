import unittest
from src.issuesignal.misinterpretation_engine import MisinterpretationEngine
from src.issuesignal.defense_generator import DefenseGenerator

class TestIS42Misinterpretation(unittest.TestCase):
    def setUp(self):
        self.risk_eng = MisinterpretationEngine()
        self.defense_gen = DefenseGenerator()

    def test_risk_detection(self):
        topic = {"title": "실적 발표 매수 추천", "urgency_score": 90}
        risks = self.risk_eng.analyze_risks(topic)
        self.assertTrue(any(r["risk_level"] == "높음" for r in risks))
        self.assertTrue(any("매수" in r["scenario"] for r in risks))

    def test_defense_generation_voice_lock(self):
        risks = [{"scenario": "수익 보장 오해", "risk_level": "높음"}]
        defense = self.defense_gen.generate_defense(risks)
        self.assertIsNotNone(defense)
        self.assertIn("아니다.", defense)
        self.assertNotIn("?", defense)
        # Should be authoritative KR
        self.assertTrue(defense.endswith("있다.") or defense.endswith("아니다."))

    def test_content_insertion(self):
        pkg = {
            "content": "이것은 본문입니다. ## 5. 결론 본문 종료.",
            "text_card": "카드 제목\n내용"
        }
        defense = "방어 문구다."
        self.defense_gen.apply_to_content(pkg, defense)
        
        self.assertIn("### ⚠️ 방어 기제", pkg["content"])
        self.assertIn(defense, pkg["content"])
        self.assertIn(f"[방어] {defense}", pkg["text_card"])

if __name__ == '__main__':
    unittest.main()
