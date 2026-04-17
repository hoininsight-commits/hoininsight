import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from src.utils.telegram_notifier import TelegramNotifier

class FactCheckerAgent:
    """
    AGENT-05.5 FACT_CHECKER
    역할: WRITER가 생성한 스크립트 내 수치 데이터 검증
    """

    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d")
        self.base_dir = Path(os.getenv("HOIN_BASE_DIR", Path(__file__).resolve().parents[2]))
        self.raw_dir = self.base_dir / f"data/raw/{self.today}"
        self.notifier = TelegramNotifier()
        
        # 엔티티 매핑 사전
        self.entity_map = {
            "vix": "vix",
            "wti": "wti_oil",
            "환율": "usd_krw",
            "달러-원": "usd_krw",
            "원-달러": "usd_krw",
            "코스피": "kospi",
            "kospi": "kospi",
            "s&p500": "sp500",
            "나스닥": "nasdaq",
            "nasdaq": "nasdaq",
            "dxy": "dxy",
            "달러인덱스": "dxy",
            "금값": "gold",
            "금": "gold",
            "10년물": "us10y",
            "국채": "us10y"
        }

    def load_reference_data(self) -> dict:
        """오늘 수집된 원천 데이터 로드"""
        data = {}
        files = ["market", "consensus", "cot"]
        for name in files:
            p = self.raw_dir / f"{name}.json"
            if p.exists():
                try:
                    data[name] = json.loads(p.read_text(encoding="utf-8"))
                except:
                    pass
        return data

    def extract_values_from_script(self, script: str) -> List[dict]:
        """
        스크립트 본문에서 수치 데이터 추출
        패턴: (엔티티) + (숫자) + (단위)
        """
        # 정규식: 숫자(소수점 포함) + 단위(%, bp, $, 배, 포인트)
        # 앞부분에 한글/영문 식별자 포함 시도
        pattern = r'([가-힣a-zA-Z0-9\-\&/\s]+?)\s*([-+]?\d*\.?\d+)\s*(%|bp|\$|배|포인트)'
        matches = re.finditer(pattern, script)
        
        extracted = []
        for m in matches:
            raw_entity = m.group(1).strip().lower()
            value = float(m.group(2))
            unit = m.group(3)
            
            # 매칭되는 엔티티 키 찾기 (동의어 처리)
            found_key = None
            for key, mapped_key in self.entity_map.items():
                if key in raw_entity:
                    found_key = mapped_key
                    break
            
            if found_key:
                extracted.append({
                    "raw": m.group(0),
                    "key": found_key,
                    "value": value,
                    "unit": unit
                })
        
        return extracted

    def verify(self, script: str) -> Tuple[bool, List[str]]:
        """수치 대조 검증"""
        ref_data = self.load_reference_data()
        if not ref_data:
            return True, ["⚠️ 참조 데이터(market.json 등)가 없어 검증을 스킵합니다."]

        market = ref_data.get("market", {}).get("data", {})
        extracted = self.extract_values_from_script(script)
        
        errors = []
        for item in extracted:
            actual_val = market.get(item["key"])
            if actual_val is None:
                continue
                
            # 오차 계산
            diff_pct = abs(item["value"] - actual_val) / actual_val if actual_val != 0 else 0
            
            if diff_pct > 0.05: # 5% 초과 시 에러
                errors.append(
                    f"\"{item['raw']}\" → 실제값: {actual_val} (오차 {diff_pct*100:.1f}%)"
                )
            else:
                # 통과 로그 (옵션)
                pass

        if errors:
            return False, errors
        return True, []

    def run(self, writer_result: dict) -> dict:
        print(f"\n🔍 AGENT-05.5 FACT_CHECKER 시작 [{self.today}]")
        
        # longform 또는 shorts 스크립트 로드
        # WriterAgent.run()은 여러 스크립트를 생성하므로, 파일 경로를 읽거나 직접 받음
        script_content = ""
        script_path = writer_result.get("longform_path")
        if script_path and os.path.exists(script_path):
            with open(script_path, "r", encoding="utf-8") as f:
                script_content = f.read()
        
        if not script_content:
            print("  ⚠️ 검증할 스크립트 내용이 없습니다.")
            return {"status": "PASS", "reason": "no_script"}

        # 날짜 확인
        # (생략: 오늘 날짜인지 체크는 이미 load_reference_data에서 raw_dir로 필터링됨)

        is_pass, report = self.verify(script_content)
        
        if is_pass:
            print("  ✅ 팩트체크 통과")
            return {"status": "PASS", "report": report}
        else:
            print(f"  ❌ 팩트체크 실패: {len(report)}건의 불일치 발견")
            
            # 알림 메시지 구성
            alert_msg = f"[FACT_CHECKER FAIL]\n검증 실패 항목:\n" + "\n".join([f"- {r}" for r in report])
            alert_msg += "\n\n발송이 차단되었습니다. 스크립트를 확인해주세요."
            
            self.notifier.send_message(alert_msg)
            
            return {"status": "FAIL", "report": report}


if __name__ == "__main__":
    # 단독 테스트용
    checker = FactCheckerAgent()
    test_script = "오늘 VIX 지수는 18.3포인트이며, WTI 유가는 $82 수준입니다."
    # 실제 데이터와 대조하려면 해당 날짜의 json이 있어야 함
    passed, logs = checker.verify(test_script)
    print(f"결과: {passed}, 로그: {logs}")
