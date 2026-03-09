import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class TopicFormatterLayer:
    """
    Step-9: Economic Hunter Topic Formatter Layer
    Refines structural topics into video-friendly narratives, hooks, and titles.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("TopicFormatterLayer")
        self.ymd = datetime.now().strftime("%Y-%m-%d")
        
    def _load_json(self, path: Path) -> Dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def _save_json(self, path: Path, data: Any):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    def refine_title(self, raw_title: str) -> str:
        # Simple rule-based refinement for example purposes
        # In a real scenario, this might involve more sophisticated logic or templates
        if "US PCE" in raw_title:
            return "지금 월가가 갑자기 인플레이션을 다시 보는 진짜 이유"
        if "Semiconductor" in raw_title:
            return "반도체 공급망 대격변, 지금 대응하지 않으면 늦는 이유"
        return f"지금 바로 주목해야 할 '{raw_title}'의 숨겨진 진실"

    def generate_hooks(self, title: str) -> Dict[str, str]:
        return {
            "hook": f"지금 월가가 갑자기 이 이슈 하나에 집착하는 이유 알고 있었어?",
            "hook_alt_1": f"모두가 놓치고 있는 {title}의 진짜 이면을 공개합니다.",
            "hook_alt_2": f"이 데이터 하나가 시장의 판도를 바꿀 겁니다. 지금 바로 확인하시죠."
        }

    def generate_video_titles(self, title_refined: str) -> Dict[str, str]:
        return {
            "title_1": title_refined,
            "title_2": f"{title_refined} (긴급 분석)",
            "title_3": f"모르면 손해 보는 {title_refined}",
            "title_4": f"월가 전문가들이 지금 이 지표에 주목하는 이유",
            "title_5": f"다음 주 시장을 주도할 '두 번째 테마'"
        }

    def run(self):
        self.logger.info(f"Running TopicFormatterLayer for {self.ymd}...")
        
        # 1. Load Structural Top-1
        top1_path = self.base_dir / "data/ops/structural_top1_today.json"
        top1_data = self._load_json(top1_path)
        
        top1_list = top1_data.get('top1_topics', [])
        if not top1_list:
            self.logger.warning("No Top-1 topic found.")
            return

        top1 = top1_list[0]
        original_card = top1.get('original_card', {})
        
        topic_id = original_card.get('topic_id', 'UNKNOWN')
        raw_title = top1.get('title', 'Untitled')
        refined_title = self.refine_title(raw_title)
        
        # 2. Economic Hunter Topic Output (D-1)
        economic_hunter_topic = {
            "topic_id": topic_id,
            "theme": original_card.get('structure_card_type', 'UNKNOWN'),
            "title_raw": raw_title,
            "title_refined": refined_title,
            "why_now": top1.get('why_now', ''),
            "mechanism": top1.get('one_line_summary', ''),
            "risk_factor": original_card.get('evidence_refs', {}).get('risk_factor', '확인 필요'),
            "confidence": "HIGH"
        }
        self._save_json(self.base_dir / "data/ops/economic_hunter_topic.json", economic_hunter_topic)

        # 3. Video Hook Output (D-2)
        video_hooks = self.generate_hooks(refined_title)
        self._save_json(self.base_dir / "data/decision/video_hook.json", video_hooks)

        # 4. Video Title Output (D-6)
        video_titles = self.generate_video_titles(refined_title)
        self._save_json(self.base_dir / "data/decision/video_titles.json", video_titles)

        self.logger.info("TopicFormatterLayer execution completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    TopicFormatterLayer(Path(__file__).resolve().parent.parent.parent).run()
