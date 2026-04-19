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
        스크립트 본문에서 수치 데이터 추출 (v7.2 패턴 기반 방식)
        """
        INDICATOR_PATTERNS = {
            'sp500': r'S&P\s*500[^\d\n]{0,20}(\d{3,5}\.?\d*)',
            'kospi': r'코스피[^\d\n]{0,20}(\d{3,5}\.?\d*)',
            'vix': r'VIX[^\d\n]{0,20}(\d{1,3}\.?\d*)',
            'wti_oil': r'WTI[^\d\n]{0,20}\$?(\d{2,3}\.?\d*)',
            'gold': r'금[^\d\n]{0,20}(\d{4,5}\.?\d*)',
            'dxy': r'달러\s*인덱스[^\d\n]{0,20}(\d{2,3}\.?\d*)',
            'us10y': r'10년물[^\d\n]{0,20}(\d{1,2}\.?\d*)',
            'usd_krw': r'환율[^\d\n]{0,20}(\d{3,4}\.?\d*)',
        }

        SKIP_PATTERNS = [
            r'\d+일',      # "90일", "20일"
            r'\d+주',      # "52주"
            r'\d+개월',    # "3개월"
            r'\d+년',      # "1년"
            r'\d+배',      # "2배"
            r'top\d+',
            r'\d+위',
        ]

        extracted = []
        
        # 1. 지표별 정밀 패턴 매칭
        for key, pattern in INDICATOR_PATTERNS.items():
            matches = list(re.finditer(pattern, script, re.IGNORECASE))
            for m in matches:
                try:
                    val = float(m.group(1).replace(',', ''))
                    # SKIP_PATTERNS에 걸리는지 확인 (값 주변 10자 이내)
                    context = script[max(0, m.start()-10):min(len(script), m.end()+10)]
                    if any(re.search(p, context) for p in SKIP_PATTERNS):
                        continue
                    
                    extracted.append({
                        "raw": m.group(1),
                        "sentence": script[max(0, m.start()-30):min(len(script), m.end()+30)].strip(),
                        "key": key,
                        "value": val,
                        "type": "TYPE_1" # 현재가로 우선 간주 (지표명+숫자 조합)
                    })
                except: continue

        # 2. Z-score 및 변화율 (기존 단순 숫자 추출 방식 유지하되 SKIP 적용)
        num_pattern = r'([-+]?\d[\d,.]*)'
        matches = list(re.finditer(num_pattern, script))
        
        for m in matches:
            start, end = m.span()
            # 이미 1단계에서 추출된 영역이면 스킵
            if any(e['key'] in script[max(0, start-15):end].lower() for e in extracted if e['type'] == 'TYPE_1'):
                # (중복 가능성 높음, 하지만 Z-score 등은 별도 추출 필요)
                pass

            # SKIP_PATTERNS 체크
            context_mid = script[max(0, start-5):min(len(script), end+5)]
            if any(re.search(p, context_mid) for p in SKIP_PATTERNS):
                continue

            try:
                raw_value = m.group(1).replace(',', '')
                if raw_value.endswith('.'): raw_value = raw_value[:-1]
                value = float(raw_value)
            except: continue

            prefix = script[max(0, start-15):start].lower()
            unit_match = re.search(r'^(%|bp|\$|배|포인트|원|계약|contracts)', script[end:])
            unit = unit_match.group(1) if unit_match else ""
            suffix = script[end + len(unit):end + 15].lower()
            
            # Z-score 탐지 (강화)
            if any(word in (prefix + suffix) for word in ["z-score", "z점수", "z-값"]):
                # 가장 가까운 엔티티 찾기
                found_key = None
                min_dist = 999
                for key, mapped_key in self.entity_map.items():
                    pos = prefix.rfind(key)
                    if pos != -1:
                        dist = len(prefix) - pos
                        if dist < min_dist:
                            min_dist = dist
                            found_key = mapped_key
                
                if found_key:
                    extracted.append({
                        "raw": f"{raw_value}{unit}",
                        "sentence": script[max(0, start-30):min(len(script), end+30)].strip(),
                        "key": found_key,
                        "value": value,
                        "type": "TYPE_3"
                    })

        return extracted

    def verify(self, script: str) -> Tuple[bool, List[str]]:
        """유형별 수치 대조 검증 (오차 허용 범위 적용)"""
        ref_data = self.load_reference_data()
        if not ref_data:
            return True, ["⚠️ 참조 데이터가 없어 검증을 스킵합니다."]

        market_data = (ref_data.get("market") or {}).get("data", {})
        extracted = self.extract_values_from_script(script)
        
        errors = []
        reports = []
        TOLERANCE = 0.05 # 5% 허용 오차
        
        type_labels = {"TYPE_1": "현재가", "TYPE_2": "변화율", "TYPE_3": "Z-score", "TYPE_4": "계약수"}

        for item in extracted:
            target_val = None
            
            if item["type"] == "TYPE_1":
                target_val = market_data.get(item["key"])
            elif item["type"] == "TYPE_3":
                stats = (market_data.get("multi_period_stats") or {}).get(item["key"], {})
                target_val = stats.get("z_score_20d")

            if target_val is None:
                continue

            match = False
            if item["type"] == "TYPE_1": # 현재가: ±5%
                if target_val != 0 and (abs(item["value"] - target_val) / abs(target_val)) <= TOLERANCE:
                    match = True
            elif item["type"] == "TYPE_3": # Z-score: ±0.3
                if abs(item["value"] - target_val) <= 0.3:
                    match = True

            type_node = type_labels.get(item["type"], "데이터")
            if match:
                reports.append(f"[{type_node}] \"{item['raw']}\" → {item['key']}: {target_val} (✅ 일치)")
            else:
                err_msg = f"[{type_node}] \"{item['raw']}\" → {item['key']}: {target_val} (❌ 불일치)"
                errors.append(err_msg)
                reports.append(err_msg)

        if errors:
            return False, reports
        return True, reports

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
            print("  ⚠️ FACT_CHECKER: 검증할 스크립트 내용 없음 — 스킵")
            return {"status": "SKIPPED", "reason": "missing_script"}

        # 참조 데이터 확인
        ref_data = self.load_reference_data()
        if not ref_data:
            print("  ⚠️ FACT_CHECKER: 참조 데이터 없음 — 스킵")
            return {"status": "SKIPPED", "reason": "missing_reference_data"}

        # 날짜 확인
        # (생략: 오늘 날짜인지 체크는 이미 load_reference_data에서 raw_dir로 필터링됨)

        is_pass, report = self.verify(script_content)
        
        if is_pass:
            print("  ✅ 팩트체크 통과")
            return {"status": "PASS", "report": report}
        else:
            print(f"  ❌ 팩트체크 실패: {len(report)}건의 불일치 발견")
            
            # 알림 메시지 구성 (텔레그렘 특수문자 오류 방지)
            clean_report = [r.replace("[", "(").replace("]", ")") for r in report]
            alert_msg = f"⚠️ (FACT_CHECKER FAIL)\n\n" + "\n".join([f"- {r}" for r in clean_report])
            alert_msg += "\n\n발송차단됨. 스크립트 확인 필요."
            
            self.notifier.send_message(alert_msg)
            
            return {"status": "FAIL", "report": report}


if __name__ == "__main__":
    # 단독 실행 모드
    checker = FactCheckerAgent()
    # 인자가 없으면 오늘 생성된 longform 스크립트를 기본으로 사용
    result = checker.run({
        "longform_path": f"data/scripts/{checker.today}/today_script_long.md"
    })
    print(f"✅ 검증 완료: {result['status']}")
    if result.get("report"):
        for r in result["report"]:
            print(f"  - {r}")
