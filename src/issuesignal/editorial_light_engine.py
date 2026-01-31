import logging
from typing import List, Dict, Any, Optional

from src.issuesignal.structural_bridge import StructuralBridge

logger = logging.getLogger("EditorialLight")

class EditorialLightEngine:
    """
    IS-70: Low-Intensity Editorial Release Layer
    고품질 콘텐츠 공백 시 매크로 구조 해설용 콘텐츠를 생성합니다.
    """

    @staticmethod
    def generate(macro_actor: Dict[str, Any], macro_state: str) -> Dict[str, Any]:
        """
        매크로 지표와 상태를 바탕으로 해설형 콘텐츠 후보를 생성합니다.
        """
        actor_name = macro_actor.get("actor_name_ko", "글로벌 매크로 자본")
        actor_tag = macro_actor.get("actor_tag", "관찰")
        
        # IS-71: Structure ID Generation
        structure_id = StructuralBridge.generate_id(macro_state, actor_name, actor_tag)
        keywords = actor_name.split() + [actor_tag, macro_state]

        # 1. Title & One Liner
        title = f"시장 구조 보고: {actor_name} 중심의 에너지 축적"
        one_liner = f"현재 시장은 단기 변동성보다 {actor_name}의 구조적 변화가 축적되는 구간에 진입했습니다."

        # ... (rest of the script steps) ...
        # [REPLACEMENT NOTE] I will keep the existing steps but ensured the return dict has new fields.
        
        script = {
            "step1": f"지금 시장에서 반복적으로 감지되는 유의미한 흐름은 {actor_name}의 움직임입니다.",
            "step2": f"대부분의 투자자가 차트의 등락에 집중하고 있으나, 본질은 이면에서 작용하는 {actor_state_desc(macro_state)}입니다.",
            "step3": f"이 신호가 아직 뉴스나 가격으로 전면 노출되지 않은 이유는 구조적 잠복기를 거치며 에너지가 응집되고 있기 때문입니다.",
            "step4": f"현재의 구조는 특정 트리거 발생 시 증폭될 수 있는 '축적형' 상태입니다. {actor_name}에게 강제되는 구조적 압력을 관찰해야 합니다.",
            "step5": "지금은 성급한 결론을 내릴 때가 아니라, 변화하는 구조의 한 축을 정확히 기억하고 대비해야 할 시점입니다."
        }

        # 3. Decision Card Data
        return {
            "structure_id": structure_id,
            "keywords": keywords,
            "summary": one_liner,
            "title": title,
            "one_liner": one_liner,
            "status": "EDITORIAL_LIGHT",
            "actor": actor_name,
            "actor_type": macro_actor.get("actor_type", "자본주체"),
            "actor_tag": actor_tag,
            "authority_sentence": one_liner,
            "decision_rationale": "최근 고품질 에디토리얼 공백이 지속됨에 따라, 현재 포착된 매크로 구조 변화를 해설형 콘텐츠로 발행합니다. (종목 도출 없음)",
            "long_form": "\n\n".join([f"{i+1}. {list(script.values())[i]}" for i in range(5)]),
            "tickers": [], # ❌ Strict Rule: No tickers for light layer
            "ticker_path": {"ticker_results": [], "global_bottleneck_ko": "구조 축적 기간이므로 특정 종목을 도출하지 않습니다."},
            "is_light": True
        }

def actor_state_desc(state: str) -> str:
    if "BULL" in state.upper(): return "강세 구조로의 점진적 전이"
    if "BEAR" in state.upper(): return "약세 압력의 체계적 확산"
    return "방향성 탐색을 위한 중립적 재편"
