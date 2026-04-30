
import json
from pathlib import Path

videos = {
    "2026/04/30": [
        ("FD8Tjeqz740", "삼성 귀족 노조의 최후?! 이재용이 직접 발표한 삼성 공장 AI로봇 대체 계획 (+수혜주)"),
        ("Aleb9BDprHM", "지금 방산 주식들이 계속 하락장인 진짜 이유"),
        ("IQISANNisek", "미국의 중국 정유사 제재.. 고래들 싸움에 한국 증시가 복 터지는 진짜 이유"),
        ("XfQWDjRqIFI", "오픈AI의 역대급 몰락이 한국 반도체 주가에 끼치는 영향")
    ],
    "2026/04/29": [
        ("dauij0Vh9nQ", "삼성전자·하이닉스 2배 ETF, 들어가기 전에 반드시 알아야 할 것"),
        ("GBqse9oamvM", "SK하이닉스 역대 7번의 저점에서 공통으로 나타난 3가지 매수 신호"),
        ("rj9x30sqzww", "예상 시기는 9월?! 월가 재산 1위가 무조건 여기에 투자하라고 콕 찝은 이유"),
        ("2XGjXaDRno0", "트럼프가 전쟁중 구글 제미나이에 역대급 자본을 쏟아붓는 진짜 이유"),
        ("uiq5EwMjxwA", "지금 실전 고수들이 몰래 줍고있다는 2차전지 저평가 종목"),
        ("dxTiv8OFacw", "지금 스페이스X 수혜주가 폭락하고 있는 진짜 이유"),
        ("7CK2cnKcEMs", "구독자 전용 종목 분석 종목: LS일렉트릭 (010120)"),
        ("e9nlgvRTLt8", "나스닥+코스피 동시 상장 역대급 상장 펼쳐 질 수있다는 한국 AI 종목 정체"),
        ("B72o1tKOHYY", "투자 고수들이 SK 하이닉스 대신, 집중 매수하고 있다는 종목")
    ]
}

RAW_BASE = Path("data/raw/youtube")

for date_path, vids in videos.items():
    for vid_id, title in vids:
        save_dir = RAW_BASE / date_path / vid_id
        save_dir.mkdir(parents=True, exist_ok=True)
        
        payload = {
            "video_id": vid_id,
            "source_id": "youtube_economic_hunter",
            "title": title,
            "published_at": date_path.replace("/", "-") + "T10:00:00+00:00",
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "channel_name": "경제사냥꾼",
            "collected_at": "2026-04-30T09:40:00Z"
        }
        
        (save_dir / "metadata.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        print(f"Created metadata for {vid_id}")
