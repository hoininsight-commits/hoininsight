SECTOR_STOCK_MAP = {
    "반도체": {
        "tickers": ["005930", "000660", "042700"],
        "names": ["삼성전자", "SK하이닉스", "한미반도체"],
        "keywords": ["HBM", "메모리", "AI반도체", "DRAM", "NAND", "sp500", "nasdaq", "증시", "주가지수", "글로벌증시"],
        "reason_templates": {
            "z_score": "sp500 Z={z_score} {direction} 주도 → 나스닥/빅테크 동반 {direction} → 한국 반도체 상관성 높음 (5d 변화율 {chg_5d}%)",
            "cot": "글로벌 기관 COT {cot_direction} 전환 → 나스닥 기술주 {direction} → 반도체 수출주 동반 영향",
            "consensus": "시장 컨센서스 {direction} → 글로벌 기술주 수요 {direction} → 메모리/HBM 수혜",
            "default": "글로벌 증시 {direction} 신호 → 나스닥/빅테크 동반 {direction} → 한국 반도체 상관성 높음"
        }
    },
    "방위": {
        "tickers": ["079550", "012450", "047810"],
        "names": ["LIG넥스원", "한화에어로스페이스", "한국항공우주"],
        "keywords": ["미사일", "천궁", "방공", "전투", "수출"],
        "reason_templates": {
            "z_score": "지정학 긴장 Z={z_score} 이상 신호 → 방산 수요 확대 기대 → 국내 방위산업 수혜",
            "cot": "원자재/에너지 COT {cot_direction} → 지정학 리스크 {direction} → 방위산업 수혜",
            "consensus": "지정학 컨센서스 {direction} → 방산 수출 기대 → 국내 방위 섹터 수혜",
            "default": "지정학 이슈 {direction} → 방산 수요 확대 기대 → 국내 방위산업 수혜"
        }
    },
    "에너지": {
        "tickers": ["010950", "096770"],
        "names": ["S-Oil", "SK이노베이션"],
        "keywords": ["유가", "정유", "원유", "LNG"],
        "reason_templates": {
            "z_score": "원유 Z={z_score} {direction} 신호 → 정제 마진 {direction} 기대 → 국내 정유사 수혜/피해",
            "cot": "원유 COT Net {cot_direction} → 유가 {direction} 전망 → 국내 정유/에너지 섹터 영향",
            "consensus": "에너지 컨센서스 {direction} → 유가 {direction} → 정유 마진 변화",
            "default": "유가 {direction} 신호 → 정제 마진 변화 → 국내 정유사 직접 영향"
        }
    },
    "금융": {
        "tickers": ["105560", "055550", "086790"],
        "names": ["KB금융", "신한지주", "하나금융지주"],
        "keywords": ["금리", "은행", "대출", "예금"],
        "reason_templates": {
            "z_score": "금리 Z={z_score} {direction} 신호 → NIM(순이자마진) {direction} 전망 → 은행주 {direction}",
            "cot": "채권 COT {cot_direction} → 금리 {direction} 전망 → 국내 은행 NIM 변화",
            "consensus": "금리 컨센서스 {direction} → 대출 수익성 {direction} → 금융주 영향",
            "default": "금리 {direction} 신호 → NIM 변화 전망 → 국내 은행주 영향"
        }
    },
    "자동차": {
        "tickers": ["005380", "000270"],
        "names": ["현대차", "기아"],
        "keywords": ["전기차", "자율주행", "관세", "수출"],
        "reason_templates": {
            "z_score": "달러 Z={z_score} {direction} → 원화 {direction_inv} → 수출 자동차 수익성 {direction}",
            "cot": "달러 COT {cot_direction} → 환율 {direction} 전망 → 자동차 수출 마진 {direction}",
            "consensus": "관세/무역 컨센서스 {direction} → 대미 수출 자동차 직접 영향",
            "default": "글로벌 경기 {direction} 신호 → 자동차 수출 수요 {direction} → 현대차/기아 영향"
        }
    },
    "바이오": {
        "tickers": ["207940", "068270"],
        "names": ["삼성바이오로직스", "셀트리온"],
        "keywords": ["임상", "FDA", "신약", "바이오시밀러"],
        "reason_templates": {
            "z_score": "헬스케어 Z={z_score} {direction} → 바이오시밀러 수요 {direction} → 국내 CDMO/바이오 수혜",
            "cot": "헬스케어 COT {cot_direction} → 글로벌 바이오 {direction} 전망 → 국내 바이오 영향",
            "consensus": "바이오 컨센서스 {direction} → 임상/FDA 기대 {direction} → 국내 바이오 섹터 영향",
            "default": "글로벌 헬스케어 {direction} 신호 → 바이오시밀러 수요 → 국내 바이오 섹터 영향"
        }
    },
    "철강": {
        "tickers": ["005490", "004020"],
        "names": ["POSCO홀딩스", "현대제철"],
        "keywords": ["철강", "LME", "철광석", "인프라"],
        "reason_templates": {
            "z_score": "철강 LME Z={z_score} {direction} → 철강 스프레드 {direction} → POSCO/현대제철 수익성 {direction}",
            "cot": "원자재 COT {cot_direction} → 철강 수요 {direction} 전망 → 국내 철강사 영향",
            "consensus": "인프라/철강 컨센서스 {direction} → LME 철강가 {direction} → 국내 철강사 수익 변화",
            "default": "LME 철강 {direction} 신호 → 글로벌 수요 {direction} → 국내 철강사 직접 영향"
        }
    },
    "알루미늄": {
        "tickers": ["014820", "001780"],
        "names": ["삼아알미늄", "KCC"],
        "keywords": ["알루미늄", "LME", "중동", "소재"],
        "reason_templates": {
            "z_score": "알루미늄 LME Z={z_score} {direction} → 소재 원가 {direction} → 국내 알루미늄 가공사 {direction}",
            "cot": "비철금속 COT {cot_direction} → 알루미늄 가격 {direction} 전망 → 소재 섹터 영향",
            "consensus": "소재 컨센서스 {direction} → LME 알루미늄 {direction} → 국내 소재사 영향",
            "default": "LME 알루미늄 {direction} 신호 → 소재 원가 변화 → 국내 알루미늄 가공사 영향"
        }
    },
    "화학": {
        "tickers": ["051910", "011170"],
        "names": ["LG화학", "롯데케미칼"],
        "keywords": ["화학", "납사", "유가", "원자재"],
        "reason_templates": {
            "z_score": "유가 Z={z_score} {direction} → 납사 원가 {direction} → 석유화학 스프레드 {direction_inv}",
            "cot": "원유 COT {cot_direction} → 납사 가격 {direction} 전망 → 화학사 마진 {direction_inv}",
            "consensus": "에너지 컨센서스 {direction} → 납사 원가 {direction} → LG화학/롯데케미칼 수익성 변화",
            "default": "유가 {direction} 신호 → 납사 원가 {direction} → 국내 화학사 마진 영향"
        }
    },
    "게임": {
        "tickers": ["036570", "259960"],
        "names": ["엔씨소프트", "크래프톤"],
        "keywords": ["게임", "출시", "신작", "모바일"],
        "reason_templates": {
            "z_score": "나스닥 Z={z_score} {direction} → 글로벌 기술주 {direction} → 국내 게임 수출주 동반 {direction}",
            "cot": "기술주 COT {cot_direction} → 글로벌 게임 섹터 {direction} 전망 → 국내 게임사 영향",
            "consensus": "기술주 컨센서스 {direction} → 글로벌 게임 수요 {direction} → 국내 게임사 수혜",
            "default": "글로벌 기술주 {direction} 신호 → 나스닥 동반 {direction} → 국내 게임 수출주 영향"
        }
    },
    "귀금속": {
        "tickers": ["010130", "000670", "103140"],
        "names": ["고려아연", "영풍", "풍산"],
        "keywords": ["Gold", "금", "귀금속", "은", "Silver", "구리", "copper", "비철금속", "제련", "스마트머니"],
        "reason_templates": {
            "z_score": "Gold Z={z_score} {direction} → 안전자산 수요 {direction} → 국내 귀금속/비철 제련사 수혜",
            "cot": "귀금속 COT Net {cot_direction} → 금/은 가격 {direction} 전망 → 고려아연/풍산 영향",
            "consensus": "안전자산 컨센서스 {direction} → 금 수요 {direction} → 국내 귀금속 섹터 수혜",
            "default": "귀금속 {direction} 신호 → 안전자산 수요 {direction} → 국내 귀금속 제련사 수혜"
        }
    }
}


def get_related_sectors(keywords: list) -> list:
    """키워드 기반 관련 섹터 반환"""
    related = []
    for sector, data in SECTOR_STOCK_MAP.items():
        if any(kw in data["keywords"] for kw in keywords):
            related.append(sector)
    return related


def get_stocks_by_sector(sector: str) -> list:
    """섹터명으로 종목 리스트 반환"""
    if sector in SECTOR_STOCK_MAP:
        return [
            {"ticker": t, "name": n}
            for t, n in zip(
                SECTOR_STOCK_MAP[sector]["tickers"],
                SECTOR_STOCK_MAP[sector]["names"]
            )
        ]
    return []


def get_reason_template(sector: str, signal_type: str) -> str:
    """섹터 + 신호 유형별 reason 템플릿 반환"""
    if sector not in SECTOR_STOCK_MAP:
        return "{direction} 신호 → {sector} 섹터 영향"
    templates = SECTOR_STOCK_MAP[sector].get("reason_templates", {})
    return templates.get(signal_type, templates.get("default", f"{{direction}} 신호 → {sector} 섹터 영향"))
