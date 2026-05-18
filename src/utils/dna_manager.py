import json
from pathlib import Path
from datetime import datetime

class DNAManager:
    """[v25.0] Economic Hunter DNA Manager - Autonomous Patching System"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).resolve().parents[2]
        self.dna_path = self.base_dir / "youtube_data/history/dna_evolution.json"
        self.patch_log_path = self.base_dir / "data/history/dna_patch_log.json"

    def get_latest_dna_patch(self, limit: int = 5) -> str:
        """최신 DNA 패치 내용들을 취합하여 프롬프트 주입용 텍스트로 반환"""
        if not self.dna_path.exists():
            return ""
            
        try:
            with open(self.dna_path, 'r', encoding='utf-8') as f:
                dna_data = json.load(f)
            
            # learned_at 기준 정렬하여 최신순으로 가져오기
            sorted_items = sorted(
                dna_data.items(), 
                key=lambda x: x[1].get('learned_at', ''), 
                reverse=True
            )
            
            patches = []
            for video_id, content in sorted_items[:limit]:
                analysis = content.get('analysis', {})
                patch = analysis.get('dna_patch', '')
                if patch:
                    patches.append(f"- {patch}")
            
            if not patches:
                return ""
                
            dna_block = "\n### [🚨 ACTIVE HUNTER DNA PATCHES]\n"
            dna_block += "\n".join(patches)
            dna_block += "\n"
            return dna_block
            
        except Exception as e:
            print(f"⚠️ [DNAManager] Failed to load DNA: {e}")
            return ""

    def get_full_dna_context(self) -> str:
        """데이터 갭, 로직 갭, 톤 갭을 포함한 상세 DNA 컨텍스트 반환"""
        if not self.dna_path.exists():
            return ""
            
        try:
            with open(self.dna_path, 'r', encoding='utf-8') as f:
                dna_data = json.load(f)
            
            latest_id, latest_content = sorted(
                dna_data.items(), 
                key=lambda x: x[1].get('learned_at', ''), 
                reverse=True
            )[0]
            
            analysis = latest_content.get('analysis', {})
            
            context = "### [ECONOMIC HUNTER DNA - CORE LOGIC]\n"
            context += f"1. Data Insights: {', '.join(analysis.get('data_gap', [])[:5])}\n"
            context += f"2. Logic Pattern: {analysis.get('logic_gap', [analysis.get('dna_patch','')])[0]}\n"
            context += f"3. Narrative Tone: {analysis.get('tone_gap', [''])[0]}\n"
            
            return context
        except:
            return ""

    def log_patch_application(self, agent_name: str):
        """패치 적용 로그 기록"""
        self.patch_log_path.parent.mkdir(parents=True, exist_ok=True)
        logs = []
        if self.patch_log_path.exists():
            try: logs = json.loads(self.patch_log_path.read_text())
            except: pass
            
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "status": "SUCCESS"
        })
        self.patch_log_path.write_text(json.dumps(logs[-100:], indent=2, ensure_ascii=False))
