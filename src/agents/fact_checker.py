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
        스크립트 본문에서 수치 데이터 추출 및 유형 분류
        """
        # 수치 패턴 (단순 숫자 + 선택적 단위)
        num_pattern = r'([-+]?\d[\d,.]*)'
        matches = list(re.finditer(num_pattern, script))
        
        extracted = []
        for m in matches:
            start, end = m.span()
            raw_value = m.group(1).replace(',', '')
            
            if not raw_value or raw_value in ['.', '-', '+']:
                continue

            try:
                # 마지막에 점으로 끝나면 제거 (문장의 마침표일 확률 높음)
                if raw_value.endswith('.'):
                    raw_value = raw_value[:-1]
                value = float(raw_value)
            except:
                continue

            # 전후 맥락 추출
            prefix = script[max(0, start-15):start].lower() # 15자로 단축 (정밀도 향상)
            unit_match = re.search(r'^(%|bp|\$|배|포인트|원|계약|contracts|건|개|시|분|만|천)', script[end:])
            unit = unit_match.group(1) if unit_match else ""
            suffix = script[end + len(unit):end + 15].lower()
            
            # 한국어 단위 처리 (예: 47만 -> 470000, 9천 -> 9000)
            if unit == "만":
                value *= 10000
                unit = ""
            elif unit == "천":
                value *= 1000
                unit = ""
            
            # 시간/수량 단위 스킵
            if unit in ["시", "분", "건", "개", "배"] and "z-score" not in prefix:
                continue
            
            # 엔티티 식별 (가장 가까운 엔티티 찾기)
            found_key = None
            min_dist = 999
            for key, mapped_key in self.entity_map.items():
                pos = prefix.rfind(key)
                if pos != -1:
                    dist = len(prefix) - pos
                    if dist < min_dist:
                        min_dist = dist
                        found_key = mapped_key
            
            # 숫자 본문에 포함된 경우 (예: "vix17")
            if not found_key:
                for key, mapped_key in self.entity_map.items():
                    if key in m.group(1).lower():
                        found_key = mapped_key
                        break
            
            if not found_key:
                continue

            # 유형 분류 (Z-score 최우선 — "상승/하락" 키워드보다 우선 적용)
            v_type = "UNKNOWN"
            context = (prefix + " " + unit + " " + suffix).strip()

            if any(word in context for word in ["z-score", "z점수", "표준편차"]):
                v_type = "TYPE_3" # Z-score (최우선)
            elif "%" in unit or any(word in context for word in ["상승", "하락", "변화", "등락", "올랐", "떨어", "5일", "주간"]):
                v_type = "TYPE_2" # 변화율
            elif any(word in context for word in ["계약", "contracts", "포지션", "매수", "매도"]):
                if unit not in ["원", "$"]:
                    v_type = "TYPE_4" # 계약수
            elif unit in ["원", "$", "포인트"] or not unit:
                if value > 50: # 가격은 보통 50 이상 (달러/포인트 등)
                    v_type = "TYPE_1" # 현재가

            if v_type != "UNKNOWN":
                extracted.append({
                    "raw": f"{raw_value}{unit}",
                    "sentence": script[max(0, start-40):min(len(script), end+40)].strip(),
                    "key": found_key,
                    "value": value,
                    "unit": unit,
                    "type": v_type
                })
        
        return extracted

    def verify(self, script: str) -> Tuple[bool, List[str]]:
        """유형별 수치 대조 검증 (오차 허용 범위 적용)"""
        ref_data = self.load_reference_data()
        if not ref_data:
            return True, ["⚠️ 참조 데이터 데이터가 없어 검증을 스킵합니다."]

        market_data = ref_data.get("market", {}).get("data", {})
        cot_data = ref_data.get("cot", {}).get("positions", {})
        
        extracted = self.extract_values_from_script(script)
        
        errors = []
        reports = []
        
        type_labels = {
            "TYPE_1": "현재가",
            "TYPE_2": "변화율",
            "TYPE_3": "Z-score",
            "TYPE_4": "계약수"
        }

        for item in extracted:
            target_val = None
            label = ""
            
            # 유형별 대조 값 및 오차 설정
            stats = market_data.get("multi_period_stats", {}).get(item["key"], {})
            
            if item["type"] == "TYPE_1":
                target_val = market_data.get(item["key"])
                label = "현재가"
            elif item["type"] == "TYPE_2":
                target_val = stats.get("chg_5d")
                label = "chg_5d"
            elif item["type"] == "TYPE_3":
                target_val = stats.get("z_score_20d")
                label = "z_score_20d"
            elif item["type"] == "TYPE_4":
                # COT 키 매핑 (표준화)
                asset_map = {
                    "gold": "Gold", 
                    "wti_oil": "WTI", 
                    "sp500": "SP500", 
                    "nasdaq": "Nasdaq",
                    "usd_krw": "USD" # 환율 COT가 있는 경우 대비
                }
                asset_key = asset_map.get(item["key"], item["key"].upper())
                target_val = cot_data.get(asset_key, {}).get("net_change")
                label = f"cot_{asset_key}"

            if target_val is None:
                reports.append(f"[{type_labels[item['type']]}] \"{item['raw']}\" → {item['key']} 데이터 없음 (스킵)")
                continue

            # 검증 수행 (지시서 기준 오차 허용)
            match = False
            diff_abs = abs(abs(item["value"]) - abs(target_val))
            
            if item["type"] == "TYPE_2": # 변화율: ±2.0%p (절대값 비교)
                if diff_abs <= 2.0: match = True
            elif item["type"] == "TYPE_3": # Z-score: ±0.3
                if abs(item["value"] - target_val) <= 0.3: match = True
            elif item["type"] == "TYPE_1": # 현재가: ±5%
                if target_val != 0 and (abs(item["value"] - target_val) / abs(target_val)) <= 0.05: match = True
            elif item["type"] == "TYPE_4": # 계약수: ±5% (절대값 비교)
                if target_val != 0 and (diff_abs / abs(target_val)) <= 0.05: match = True
                elif target_val == 0 and diff_abs < 100: match = True

            type_name = type_labels[item['type']]
            if match:
                reports.append(f"[{type_name}] \"{item['raw']}\" → {label}: {target_val} (✅ 일치)")
            else:
                err_msg = f"[{type_name}] \"{item['raw']}\" → {label}: {target_val} (❌ 불일치)"
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
            
            # 알림 메시지 구성 (텔레그렘 특수문자 오류 방지)
            clean_report = [r.replace("[", "(").replace("]", ")") for r in report]
            alert_msg = f"⚠️ (FACT_CHECKER FAIL)\n\n" + "\n".join([f"- {r}" for r in clean_report])
            alert_msg += "\n\n발송차단됨. 스크립트 확인 필요."
            
            self.notifier.send_message(alert_msg)
            
            return {"status": "FAIL", "report": report}


if __name__ == "__main__":
    # 단독 테스트용
    checker = FactCheckerAgent()
    test_script = "오늘 VIX 지수는 18.3포인트이며, WTI 유가는 $82 수준입니다."
    # 실제 데이터와 대조하려면 해당 날짜의 json이 있어야 함
    passed, logs = checker.verify(test_script)
    print(f"결과: {passed}, 로그: {logs}")
