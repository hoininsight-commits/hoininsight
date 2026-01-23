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
        risk = topic.get('risk_note', '시장 변동성 확대')
        
        # New Analytical Template
        # 1. Status Summary
        status = f"[시장 분석] 현재 {anchor} 현상이 포착되었으며, 이는 {trigger} 상황을 핵심 분기점으로 하고 있습니다."
        
        # 2. Key Evidence
        metric_text = ", ".join(metrics)
        evidence = f"[데이터 증거] 주요 관측 지표인 {metric_text}의 움직임이 전형적인 흐름을 벗어나며 새로운 경제적 파급력을 시사하고 있습니다."
        
        # 3. Core Driver Analysis
        analysis = f"[핵심 동인 분석] 이번 현상의 기저에는 '{driver}'가 자리 잡고 있습니다. 이는 단순한 일시적 변동이 아닌, 시장의 유동성 흐름이나 정책적 기조가 새로운 국면에 진입했음을 의미합니다."
        
        # 4. Outlook & Implications
        outlook = f"[전망 및 시사점] 전문 투자 기관들은 이미 이러한 변화를 반영하여 자산 재배분 및 리스크 관리에 착수했습니다. 표면적인 가격 변동보다는 그 이면의 가치 사슬 변화가 장기적 수익성을 결정할 것입니다."
        
        # 5. Risk Assessment & Conclusion
        conclusion = f"[리스크 관리] 다만, {risk} 시나리오가 현실화될 경우 단기적 변동성이 커질 수 있으므로 신중한 모니터링이 필요합니다. 호인 엔진은 지속적으로 관련 데이터를 비교 분석하여 전략적 인사이트를 제공하겠습니다."
        
        full_script = f"""{status}

{evidence}

{analysis}

{outlook}

{conclusion}"""
        
        return full_script
