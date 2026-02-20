"""
IS-95-4 Price Mechanism Collector
Collects indicators for Structural Pricing Power and Rigidity.
"""
import json
from pathlib import Path
from datetime import datetime
import random

class PriceMechanismCollector:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent.parent
        self.collect_dir = self.base_dir / "data" / "collect"
        self.collect_dir.mkdir(parents=True, exist_ok=True)

    def collect_price_spreads(self):
        """
        Collects Spot vs Contract price spreads.
        Proxy: Generating deterministic sample data for MVP.
        """
        data = {
            "sector": "SEMICONDUCTORS",
            "as_of": datetime.now().strftime("%Y-%m-%d"),
            "items": [
                {
                    "item": "HBM3E",
                    "contract_price_index": 120.0,
                    "spot_price_index": 145.0,
                    "spread_ratio": 1.20, # Spot > Contract = Bullish/Shortage
                    "margin_proxy_supplier": 0.45,
                    "margin_proxy_buyer": 0.15
                },
                {
                    "item": "Legacy DDR4",
                    "contract_price_index": 90.0,
                    "spot_price_index": 85.0,
                    "spread_ratio": 0.94, # Oversupply
                    "margin_proxy_supplier": 0.10,
                    "margin_proxy_buyer": 0.20
                }
            ]
        }
        self._save("price_spread_indicators.json", data)

    def collect_backlog(self):
        """
        Collects Order Backlog and Utilization.
        """
        data = {
            "sector": "POWER_INFRA",
            "as_of": datetime.now().strftime("%Y-%m-%d"),
            "items": [
                {
                    "segment": "Transformers",
                    "backlog_ratio": 3.5, # Years of backlog
                    "capacity_utilization": 0.98,
                    "lead_time_months": 48,
                    "allocation_flag": True
                },
                {
                    "segment": "Cables",
                    "backlog_ratio": 1.2,
                    "capacity_utilization": 0.85,
                    "lead_time_months": 12,
                    "allocation_flag": False
                }
            ]
        }
        self._save("order_backlog_utilization.json", data)

    def collect_dependency(self):
        """
        Collects Buyer Dependency Index.
        """
        data = {
            "sector": "AI_HARDWARE",
            "as_of": datetime.now().strftime("%Y-%m-%d"),
            "items": [
                {
                    "buyer_segment": "Hyperscalers",
                    "top_supplier_concentration": 0.90, # NVDA/TSMC
                    "tech_lock_in_flag": True,
                    "certification_required_flag": True
                }
            ]
        }
        self._save("buyer_dependency_index.json", data)

    def _save(self, filename, data):
        path = self.collect_dir / filename
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[PRICE_MECH] Saved {filename}")

    def run(self):
        self.collect_price_spreads()
        self.collect_backlog()
        self.collect_dependency()

if __name__ == "__main__":
    collector = PriceMechanismCollector()
    collector.run()
