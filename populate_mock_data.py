
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from src.learning.deep_logic_analyzer import DeepLogicAnalyzer
from src.utils.knowledge_base import KnowledgeBase

def populate_mock_data():
    base_dir = Path(os.getcwd())
    ymd = datetime.utcnow().strftime("%Y-%m-%d")
    ymd_path = ymd.replace("-", "/")
    
    # 1. Populate Deep Logic Analysis (The "Transformer" Report)
    print("1. Generatign Deep Logic Mock Data...")
    kb = KnowledgeBase(base_dir)
    analyzer = DeepLogicAnalyzer(kb)
    
    # Use the verified ChatGPT-style transcript
    video_id = "mock_supercycle_01"
    title = "[긴급진단] 전력 인프라, 지금이 마지막 탑승 기회인가? (feat. 변압기 슈퍼사이클)"
    transcript = """
    (User provided script from ChatGPT conversation - inferred context)
    
    최근 전력 인프라 관련해서 '변압기 슈퍼사이클' 이야기가 많이 나오는데, 이게 단순한 테마가 아니라 구조적인 변화라는 증거들이 보입니다.
    
    1. 미국 유틸리티 회사들의 CAPEX 계획이 10년 만에 최대치로 상향되었습니다. 
       듀크 에너지나 엑셀론 같은 기업들이 향후 5년간 송전망 현대화에만 수백억 달러를 쏟아붓겠다고 공시했죠.
       이는 정부의 IRA 보조금과 맞물려서 '집행되지 않을 수 없는 예산' 성격이 강합니다.
    
    2. 그리고 변압기 리드타임(주문 후 인도까지 걸리는 시간)이 2021년 12개월에서 현재 36개월, 일부 고압 변압기는 48개월까지 늘어났습니다.
       이건 단순히 수요가 좀 늘어난 수준이 아니라, 공급망 자체가 락인(Lock-in)되었다는 뜻입니다.
       지금 주문해도 4년 뒤에나 받는다면, 지금의 수주 잔고는 향후 4년치 매출이 확정된 것이나 다름없죠.
    
    3. 또 하나, 데이터센터 전력 소비량이 기하급수적으로 늘고 있습니다.
       엔비디아 칩을 아무리 사도 전기가 없으면 못 돌립니다.
       지금 미국 버지니아 주 같은 데이터센터 밀집 지역에서는 전력 공급 승인이 안 나서 데이터센터 착공이 지연되고 있어요.
       이건 '전력망'이 AI 산업의 가장 큰 병목(Bottleneck)이 되었다는 확실한 신호입니다.
       
    결론적으로 이건 '기대감'으로 오르는 주식 테마가 아니라, '필수불가결한 인프라'로서 자본이 강제로 집행되어야 하는 섹터라고 봅니다.
    주가가 많이 올랐다고 하지만, 실적 성장 속도가 더 빠르기 때문에 여전히 저평가 국면일 수 있습니다.
    """
    
    # Run Analysis (This calls Gemini if key is present, otherwise heuristics)
    # Ideally we use the SAVED report if possible to save Quota, but let's run it once to be sure it saves correctly.
    # To save quota, I will mock the LLM result part if I can, OR just run it. 
    # Since user complained about Quota, let's TRY to perform analysis.
    # But wait, I have the LLM report in the logs? No, I can't easily retrieve it.
    # I will run it, but just one.
    
    if os.getenv("GEMINI_API_KEY"):
        result = analyzer.analyze(video_id, title, transcript)
        
        # Save it
        output_dir = base_dir / "data/narratives/deep_analysis" / ymd_path
        output_dir.mkdir(parents=True, exist_ok=True)
        analyzer.save_report(result, output_dir)
        print(f"   [Saved] Deep Logic Analysis for {video_id}")
    else:
        print("   [Skip] No API Key for Deep Logic")

    # 1.5 Populate Evolution Proposals (Mocking the Parser Result)
    print("1.5 Populating Evolution Proposals...")
    evo_dir = base_dir / "data/evolution/proposals"
    evo_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock Proposal 1 (Logic Update)
    p1 = {
        "id": "EVO-MOCK-20260119-00001",
        "generated_at": datetime.utcnow().isoformat(),
        "category": "LOGIC_UPDATE",
        "status": "PROPOSED",
        "content": {
            "condition": "Supply Chain Bottleneck detected",
            "meaning": "Transformer Lead Time > 36 months implies Structural L3 Anomaly"
        },
        "evidence": {
            "quote": "변압기 리드타임이 36개월에서 48개월로 늘어남",
            "source": title
        }
    }
    
    # Mock Proposal 2 (Data Add - The Engine Suggestion)
    p2 = {
        "id": "EVO-MOCK-20260119-00002",
        "generated_at": datetime.utcnow().isoformat(),
        "category": "DATA_ADD",
        "status": "PROPOSED",
        "content": {
            "condition": "Sector CAPEX Tracker",
            "meaning": "This sensor proves the lock-in by tracking utility major CAPEX execution rates vs plans."
        },
        "evidence": {
            "quote": "New specific sensor needed for sector capex",
            "source": title
        }
    }
    
    (evo_dir / "EVO-MOCK-001.json").write_text(json.dumps(p1, ensure_ascii=False, indent=2), encoding='utf-8')
    (evo_dir / "EVO-MOCK-002.json").write_text(json.dumps(p2, ensure_ascii=False, indent=2), encoding='utf-8')

    # 2. Populate Youtube Inbox (Mock)
    print("2. Populating Youtube Inbox...")
    inbox_dir = base_dir / "data/narratives/inbox" / ymd_path
    inbox_dir.mkdir(parents=True, exist_ok=True)
    
    inbox_data = [
        {
            "video_id": "mock_vid_01",
            "title": "비트코인 1억 돌파, 알트코인 불장 언제 오나?",
            "channel": "CryptoKing",
            "published_at": datetime.utcnow().isoformat() + "Z",
            "view_count": 50000,
            "status": "COLLECTED"
        },
        {
            "video_id": "mock_vid_02",
            "title": "삼성전자 실적 쇼크, 반도체 바닥론 점검",
            "channel": "StockMaster",
            "published_at": datetime.utcnow().isoformat() + "Z",
            "view_count": 12000,
            "status": "COLLECTED"
        },
        {
            "video_id": "mock_vid_03",
            "title": "Fed 금리 인하, 환율 1200원대 가능할까?",
            "channel": "MacroSight",
            "published_at": datetime.utcnow().isoformat() + "Z",
            "view_count": 30000,
            "status": "COLLECTED"
        }
    ]
    (inbox_dir / "videos.json").write_text(json.dumps(inbox_data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    # 3. Populate Narrative Status (To show INGESTION_OK)
    status_dir = base_dir / "data/narratives/status" / ymd_path
    status_dir.mkdir(parents=True, exist_ok=True)
    status_data = {
        "videos_detected": 3,
        "transcript_ok": 3,
        "deep_analysis_count": 1
    }
    (status_dir / "collection_status.json").write_text(json.dumps(status_data, ensure_ascii=False, indent=2), encoding='utf-8')

    print("Done. Mock data populated.")

if __name__ == "__main__":
    populate_mock_data()
