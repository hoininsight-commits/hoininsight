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
        misconception = topic.get("public_misconception", "일반적인 거시 경제적 관점")
        money_flow = topic.get("money_flow", "시장의 자금 순환 흐름")
        baseline = topic.get("comparison_baseline", "역사적 평균 범주")
        risk = topic.get('risk_note', '시장 변동성 확대')
        
        # New Analytical Template with strict requirements
        # 1. Status Summary & Misconception
        status = f"[시장 분석] 현재 {anchor} 현상이 포착되었습니다. 대중은 주로 '{misconception}'에 매몰되어 있으나, 실질적인 데이터는 전혀 다른 방향을 가리키고 있습니다."
        
        # 2. Key Evidence & Baseline
        metric_text = ", ".join(metrics)
        evidence = f"[데이터 증거] {metric_text} 지표는 {baseline}과 비교했을 때 매우 이례적인 수준에 도달했으며, 이는 {trigger} 상황이 단순 현상을 넘어 실질적 국면 전환임을 시사합니다."
        
        # 3. Core Driver & Money Flow
        analysis = f"[핵심 분석] 이번 현상을 관통하는 자본의 실질적 이동은 '{money_flow}'로 확인됩니다. 기저의 핵심 동인은 '{driver}'이며, 이는 시장의 질서가 재편되고 있음을 의미합니다."
        
        # 4. Outlook & Implications
        outlook = f"[전망 및 시사점] 전문 투자 기관들은 이미 이 흐름을 포착하고 자산 재배분을 시작했습니다. 표면적인 노이즈를 걷어내고 실질적 자본의 이동 경로에 주목해야 할 시점입니다."
        
        # 5. Risk Assessment & Conclusion
        conclusion = f"[리스크 관리] {risk} 가능성에 항시 유의하시기 바랍니다. 호인 엔진은 데이터에 근거한 객관적 지표만을 통해 가치 있는 인사이트를 지속적으로 제공하겠습니다."
        
        full_script = f"""{status}

{evidence}

{analysis}

{outlook}

{conclusion}"""
        
        return full_script
