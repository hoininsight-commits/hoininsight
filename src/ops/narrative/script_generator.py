import json

class ScriptGenerator:
    def generate_scripts(self, narrative_topics_data):
        """
        Generates 60-120s script for each topic.
        """
        topics = narrative_topics_data.get("topics", [])
        
        for t in topics:
            script = self._create_script(t)
            t["script_kr"] = script
            
        return narrative_topics_data

    def _create_script(self, topic):
        anchor = topic["topic_anchor"]
        driver = topic["narrative_driver"]
        trigger = topic["trigger_event"]
        metrics = topic["observed_metrics"]
        
        # Template Application
        # 1. Hook
        hook = f"님들 지금 {anchor} 때문에 난리 난 거 진짜 이유 알고 있어? 다들 {trigger} 보고 대단하다 하는데 진짜 중요한 건 따로 있어. 내가 딱 1분 만에 정리해 줄게."
        
        # 2. Observation
        metric_text = ", ".join(metrics)
        obs = f"지금 데이터를 보면 {metric_text} 같은 숫자들이 찍히고 있어. 겉보기엔 그냥 이슈 같지만 이건 표면적인 이유일 뿐이야."
        
        # 3. Driver
        driver_sec = f"진짜 핵심은 '{driver}'야. 이게 무슨 뜻이냐면, 시장의 돈이 움직이는 규칙 자체가 바뀌었다는 소리야."
        
        # 4. Implication
        imp = f"월가는 이미 이 흐름을 보고 재평가에 들어갔어. 단순히 기대감이 아니라 실제로 숫자가 찍히는 곳으로 자본이 쏠리고 있다는 거지."
        
        # 5. Risk
        risk = f"물론 리스크는 있어. {topic.get('risk_note','반대 시나리오')}가 발생하면 조정이 올 수도 있어."
        
        # 6. Close
        close = "결국 우리가 봐야 할 건 돈의 흐름이 어디로 고정되느냐야. 경제사냥꾼 구독하고 진짜 부자 되자."
        
        full_script = f"""[00:00] {hook}
[00:10] {obs}
[00:30] {driver_sec}
[01:10] {imp}
[01:35] {risk}
[01:50] {close}"""
        
        return full_script
