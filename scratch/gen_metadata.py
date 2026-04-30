import json
from pathlib import Path

videos = {
    "2026/04/30": [
        ("jYU7NkESKkE", "이재용 회장이, 노조 파업에도 '버티고 있는' 진짜 이유")
    ],
    "2026/04/28": [
        ("wyXybqB9ggI", "투자자들이 반드시 알아야 할 '금' 전망+투자 포인트"),
        ("wl_JDcheBWc", "코스피 상승장 속, 주가 2배 가까이 올랐다는 '대통령 포트폴리오' 수익률"),
        ("V3Pi86vfds0", "경제사냥꾼 구독자 전용, 종목 분석 : LG전자"),
        ("c-UUPuaXYwA", "시총 6000조 시대.. '국장' 이끌고 갈 수 있다는 기업 3곳"),
        ("mksitWsvGBk", "지금 상위 0.1% 투자자들이 쓸어 담고 있다는 '반도체' ETF")
    ],
    "2026/04/27": [
        ("WT2kVO-ZYi4", "3050 투자 고수들이, 자녀 계좌에 '남몰래 담고 있다'는 종목과 방법"),
        ("KnziUrXipiY", "깐부 회동 만든 '젠슨황 딸' 매디슨 황이 한국에서 찾고 있는 '종목들' 정체"),
        ("eLmAlH2k-Ys", "연준 의장 '파월' 퇴임이 '한국 투자자'들에게 진짜 '기회'인 이유"),
        ("WYkyN5DzYWw", "이번주 '빅테크' 실적 발표로 역대급 주가 '상승장' 올 수 있다는 이유(+투자 포인트 총정리)"),
        ("Ex_Em7cMybg", "경제사냥꾼 구독자 전용, 종목 분석 : 두산에너빌리티"),
        ("fwOwPGfLph0", "월가에서 '코스닥 3000' 상승장 이끌고 갈 수 있다는 종목 TOP3")
    ],
    "2026/04/26": [
        ("hMW-cLS4y4A", "삼성전자, 하이닉스 역대급 실적 속, 월가에서 긴급 '하락'장 경고하는 진짜 이유")
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
            "collected_at": "2026-04-30T10:00:00Z"
        }
        
        (save_dir / "metadata.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        print(f"Created metadata for {vid_id}")
