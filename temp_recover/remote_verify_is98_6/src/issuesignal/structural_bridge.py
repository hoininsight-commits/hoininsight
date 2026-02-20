import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("StructuralBridge")

class StructuralBridge:
    """
    IS-71: Structural Continuity Bridge Engine
    과거의 구조 해설(EDITORIAL_LIGHT)과 현재의 실데이터(HARD_FACT)를 연결합니다.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.memory_path = base_dir / "data" / "memory" / "structural_memory.json"
        self._ensure_storage()

    def _ensure_storage(self):
        if not self.memory_path.exists():
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    @staticmethod
    def generate_id(theme: str, actor: str, sector: str) -> str:
        """구조 ID 생성 (해시 조합)"""
        raw = f"{theme}_{actor}_{sector}".upper()
        return hashlib.md5(raw.encode()).hexdigest()[:12]

    def record_structure(self, structure_data: Dict[str, Any]):
        """새로운 구조 해설을 메모리에 기록"""
        memory = self._load_memory()
        
        # 중복 확인
        if any(m['structure_id'] == structure_data['structure_id'] for m in memory):
            return

        memory.append({
            "structure_id": structure_data['structure_id'],
            "timestamp": datetime.now().isoformat(),
            "summary": structure_data['summary'],
            "actor": structure_data.get('actor', '').upper(),
            "sector": structure_data.get('sector', '').upper(),
            "keywords": [k.upper() for k in structure_data.get('keywords', [])],
            "status": "ACTIVE"
        })
        self._save_memory(memory)

    def find_bridge(self, current_event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """현재 이벤트와 매칭되는 과거 구조 탐색"""
        memory = self._load_memory()
        active_structures = [m for m in memory if m['status'] == "ACTIVE"]
        
        curr_actor = str(current_event.get('actor', '')).upper()
        curr_sector = str(current_event.get('sector', '')).upper()
        curr_text = str(current_event.get('fact_text', '')).upper()

        for struct in active_structures:
            # 1. Actor/Sector 매칭
            actor_match = curr_actor != "" and curr_actor == struct['actor']
            sector_match = curr_sector != "" and curr_sector == struct['sector']
            
            # 2. 키워드 매칭
            keyword_match = any(kw in curr_text for kw in struct['keywords'])

            if actor_match or sector_match or keyword_match:
                # 브릿지 성립
                days_ago = (datetime.now() - datetime.fromisoformat(struct['timestamp'])).days
                
                # 상태 업데이트 (RESOLVED로 변경하지 않고 유지할 수도 있으나 스펙상 현실화 전이)
                # 여기서는 정보만 반환하고 상태 변경은 run_issuesignal에서 결정하도록 함
                return {
                    "structure_id": struct['structure_id'],
                    "days_ago": days_ago,
                    "original_summary": struct['summary'],
                    "timestamp": struct['timestamp']
                }
        
        return None

    def resolve_structure(self, structure_id: str):
        """구조 상태를 RESOLVED로 변경"""
        memory = self._load_memory()
        for struct in memory:
            if struct['structure_id'] == structure_id:
                struct['status'] = "RESOLVED"
                struct['resolved_at'] = datetime.now().isoformat()
                break
        self._save_memory(memory)

    def _load_memory(self) -> List[Dict[str, Any]]:
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def _save_memory(self, memory: List[Dict[str, Any]]):
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
