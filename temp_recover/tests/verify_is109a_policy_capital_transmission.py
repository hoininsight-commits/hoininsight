import unittest
import json
import re
from pathlib import Path
from src.ui.policy_capital_transmission import PolicyCapitalTransmission

class TestIS109APolicyCapitalTransmission(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(".")
        self.output_json = self.base_dir / "data" / "ui" / "policy_capital_transmission.json"
        
        # 엔진 실행
        engine = PolicyCapitalTransmission(self.base_dir)
        engine.run()

    def test_output_exists(self):
        self.assertTrue(self.output_json.exists(), "policy_capital_transmission.json이 생성되지 않았습니다.")

    def test_schema_keys(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        required_keys = [
            "date", "status", "signal_type", "money_nature", "time_to_money", 
            "price_floor", "headline", "one_liner", "mechanism", 
            "numbers_with_evidence", "who_gets_paid_first", "risk_note", "guards"
        ]
        for key in required_keys:
            self.assertIn(key, data, f"필수 키 {key}가 누락되었습니다.")

    def test_no_undefined(self):
        content = self.output_json.read_text(encoding='utf-8')
        self.assertNotIn("undefined", content.lower(), "JSON에 'undefined' 문자열이 포함되어 있습니다.")

    def test_numbers_and_citations(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        
        # numbers_with_evidence 검사
        for n in data["numbers_with_evidence"]:
            if "데이터 확인 중" not in n:
                self.assertTrue(re.search(r'\d', n), f"숫자가 포함되지 않았습니다: {n}")
                self.assertTrue(re.search(r'\(.*\)', n), f"출처(괄호)가 포함되지 않았습니다: {n}")

        # mechanism 검사
        for m in data["mechanism"]:
            self.assertTrue(re.search(r'\(.*\)', m), f"근거(괄호)가 포함되지 않았습니다: {m}")

    def test_who_gets_paid_first_keys(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        who = data["who_gets_paid_first"]
        for key in ["PICKAXE", "BOTTLENECK", "HEDGE"]:
            self.assertIn(key, who)
            self.assertIsInstance(who[key], list)

    def test_whitelist_citations_integrity(self):
        # citations 파일의 허용된 소스들과 결과물의 출처가 매칭되는지 확인 (간이 검증)
        citations_path = self.base_dir / "data" / "decision" / "evidence_citations.json"
        citations_data = json.loads(citations_path.read_text(encoding='utf-8'))
        
        whitelisted_tags = set()
        for doc in citations_data:
            for cit in doc.get("citations", []):
                whitelisted_tags.add(cit.get("evidence_tag"))
        
        # 추가로 'Internal Source', 'Market Analytics' 등 엔진 내부 화이트리스트 허용
        allowed_sources = whitelisted_tags | {"Internal Source", "Market Analytics", "WHITELIST", "Internal Docs"}
        
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        all_text = json.dumps(data, ensure_ascii=False)
        
        # 괄호 안의 소스 추출
        sources_in_result = re.findall(r'\((.*?)\)', all_text)
        for src in sources_in_result:
            # 날짜 형식은 제외 (YYYY-MM-DD)
            if re.match(r'\d{4}-\d{2}-\d{2}', src): continue
            
            # 허용된 태그 또는 소스 문자열이 포함되어 있는지 확인
            is_valid = any(tag in src for tag in allowed_sources)
            self.assertTrue(is_valid, f"허용되지 않은 출처가 발견되었습니다: {src}")

if __name__ == "__main__":
    unittest.main()
