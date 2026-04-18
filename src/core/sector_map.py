SECTOR_STOCK_MAP = {
    "반도체": {
        "tickers": ["005930", "000660", "042700"],
        "names": ["삼성전자", "SK하이닉스", "한미반도체"],
        "keywords": ["HBM", "메모리", "AI반도체", "DRAM", "NAND", "sp500", "nasdaq", "증시", "주가지수", "글로벌증시"]
    },
    "방위": {
        "tickers": ["079550", "012450", "047810"],
        "names": ["LIG넥스원", "한화에어로스페이스", "한국항공우주"],
        "keywords": ["미사일", "천궁", "방공", "전투", "수출"]
    },
    "에너지": {
        "tickers": ["010950", "096770"],
        "names": ["S-Oil", "SK이노베이션"],
        "keywords": ["유가", "정유", "원유", "LNG"]
    },
    "금융": {
        "tickers": ["105560", "055550", "086790"],
        "names": ["KB금융", "신한지주", "하나금융지주"],
        "keywords": ["금리", "은행", "대출", "예금"]
    },
    "자동차": {
        "tickers": ["005380", "000270"],
        "names": ["현대차", "기아"],
        "keywords": ["전기차", "자율주행", "관세", "수출"]
    },
    "바이오": {
        "tickers": ["207940", "068270"],
        "names": ["삼성바이오로직스", "셀트리온"],
        "keywords": ["임상", "FDA", "신약", "바이오시밀러"]
    },
    "철강": {
        "tickers": ["005490", "004020"],
        "names": ["POSCO홀딩스", "현대제철"],
        "keywords": ["철강", "LME", "철광석", "인프라"]
    },
    "알루미늄": {
        "tickers": ["014820", "001780"],
        "names": ["삼아알미늄", "KCC"],
        "keywords": ["알루미늄", "LME", "중동", "소재"]
    },
    "화학": {
        "tickers": ["051910", "011170"],
        "names": ["LG화학", "롯데케미칼"],
        "keywords": ["화학", "납사", "유가", "원자재"]
    },
    "게임": {
        "tickers": ["036570", "259960"],
        "names": ["엔씨소프트", "크래프톤"],
        "keywords": ["게임", "출시", "신작", "모바일"]
    },
    "귀금속": {
        "tickers": ["010130", "000670", "103140"],
        "names": ["고려아연", "영풍", "풍산"],
        "keywords": ["Gold", "금", "귀금속", "은", "Silver", "구리", "copper", "비철금속", "제련", "스마트머니"]
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
