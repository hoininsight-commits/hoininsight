from typing import Dict, Any, List
from src.tickers.company_map_registry import BOTTLENECK_SLOT_MAP, Step3BottleneckSignal
from src.tickers.reality_filter import run_reality_filter
from src.tickers.guardrail import run_guardrail
from src.tickers.monopoly_pressure_score import run_monopoly_pressure_score

class TickerLinkerEngine:
    def run(self, signal: Step3BottleneckSignal) -> Dict[str, Any]:
        """
        Execute Step 4 Pipeline.
        """
        # 1. Registry Lookup
        raw_candidates = BOTTLENECK_SLOT_MAP.get(signal.bottleneck_slot, [])
        
        if not raw_candidates:
            return self._create_reject_card(signal, "No candidates in registry for this bottleneck.")
            
        # 2. Reality Filter
        real_candidates, reality_rejects = run_reality_filter(raw_candidates)
        if not real_candidates:
             return self._create_reject_card(signal, f"All candidates failed Reality Check: {'; '.join(reality_rejects)}")

        # 3. Guardrail (Anti-Hallucination)
        valid_candidates, guardrail_rejects = run_guardrail(real_candidates)
        if not valid_candidates:
            return self._create_reject_card(signal, f"All candidates failed Guardrail: {'; '.join(guardrail_rejects)}")
            
        # 4. Monopoly Pressure Score
        decision, final_candidates, reject_reason = run_monopoly_pressure_score(valid_candidates)
        
        if decision == "REJECT":
            return self._create_reject_card(signal, reject_reason)
            
        # 5. Build Locked Card
        return self._create_locked_card(signal, final_candidates)

    def _create_reject_card(self, signal: Step3BottleneckSignal, reason: str) -> Dict[str, Any]:
        return {
            "card_type": "LOCKED_TICKER_CARD",
            "status": "REJECT",
            "trigger_context": {
                "type": "UNKNOWN", # Passed from signal but simplified here
                "event": signal.trigger,
                "timestamp": "Today"
            },
            "structural_logic": {
                "forced_capex": signal.forced_capex,
                "bottleneck_def": signal.bottleneck_slot
            },
            "reject_reason": reason,
            "tickers": []
        }

    def _create_locked_card(self, signal: Step3BottleneckSignal, candidates: List[Any]) -> Dict[str, Any]:
        tickers_out = []
        full_kill_switch = []
        
        for c in candidates:
            tickers_out.append({
                "ticker": c.tickers,
                "name": c.company_name,
                "role": c.bottleneck_role,
                "why_irreplaceable_now": c.irreplaceable_now,
                "evidence": c.fact_tokens
            })
            if c.kill_switch:
                full_kill_switch.append(f"{c.company_name}: {c.kill_switch}")
                
        return {
            "card_type": "LOCKED_TICKER_CARD",
            "status": "LOCKED",
            "trigger_context": {
                "type": "MAPPED_FROM_STEP2", # Mock
                "event": signal.trigger,
                "timestamp": "Today"
            },
            "structural_logic": {
                "forced_capex": signal.forced_capex,
                "bottleneck_def": signal.bottleneck_slot
            },
            "tickers": tickers_out,
            "kill_switch": " | ".join(full_kill_switch)
        }
