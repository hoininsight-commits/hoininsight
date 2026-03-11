from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class CandidateCompany:
    company_name: str
    tickers: List[str]  # e.g. ["009540.KS"]
    bottleneck_role: str
    fact_tokens: List[str]  # Internal hard-fact strings
    
    # Reality Filter Flags (Default True)
    revenue_exists: bool = True
    delivery_record: bool = True
    certification: bool = True
    capacity_scale: bool = True
    leadtime_ok: bool = True
    
    # Metadata
    kill_switch: str = ""
    irreplaceable_now: str = ""
    
    # Scoring Proxy (0-10)
    market_share_proxy: int = 0
    expansion_speed_proxy: int = 0

@dataclass
class Step3BottleneckSignal:
    trigger: str
    forced_capex: str
    bottleneck_slot: str

# MOCK REGISTRY for Step 4
# In real life, this would be a database or a larger config file.

BOTTLENECK_SLOT_MAP: Dict[str, List[CandidateCompany]] = {
    # Scenario 1: Green Ship Core (Policy Trigger)
    "GREEN_SHIP_CORE_SYSTEM": [
        CandidateCompany(
            company_name="HD Hyundai Heavy Industries",
            tickers=["009540.KS"],
            bottleneck_role="Global #1 Engine & Ship Builder",
            fact_tokens=["FACT_ENGINE_MKT_SHARE_35", "FACT_BACKLOG_3Y", "FACT_DUAL_FUEL_LICENSE", "FACT_HIMSEN_ENGINE"],
            irreplaceable_now="Holds >35% global market share in dual-fuel engines; Docks fully booked for 3 years.",
            kill_switch="Global recession causes shipping rates (SCFI) to crash below break-even.",
            market_share_proxy=9,
            expansion_speed_proxy=7
        ),
        CandidateCompany(
            company_name="Hanwha Ocean",
            tickers=["042660.KS"],
            bottleneck_role="LNG Carrier Specialist",
            fact_tokens=["FACT_BACKLOG_3Y", "FACT_LNG_TECH", "FACT_QATAR_DEAL"],
            irreplaceable_now="Strongest LNG carrier tech; secured massive Qatar LNG deal.",
            kill_switch="Labor shortage delays delivery significantly.",
            market_share_proxy=7,
            expansion_speed_proxy=6
        ),
        CandidateCompany(
            company_name="Samsung Heavy Industries",
            tickers=["010140.KS"],
            bottleneck_role="FLNG Leader",
            fact_tokens=["FACT_BACKLOG_2Y", "FACT_FLNG_LEADER"],
            irreplaceable_now="Dominant in FLNG market.",
            kill_switch="Offshore project cancellation.",
            market_share_proxy=7,
            expansion_speed_proxy=5
        ),
        CandidateCompany(
            company_name="Small Ship Parts Co",
            tickers=["999999.KS"],
            bottleneck_role="Parts Supplier",
            fact_tokens=[], # No facts
            revenue_exists=False, # Fail
            delivery_record=False, # Fail
            irreplaceable_now="Hoping to supply.",
            kill_switch="Bankruptcy",
            market_share_proxy=1
        )
    ],

    # Scenario 2: HV Transformer (Supply Chain Trigger)
    "HV_TRANSFORMER_LEADTIME": [
        CandidateCompany(
            company_name="HD Hyundai Electric",
            tickers=["267260.KS"],
            bottleneck_role="Key US Vendor",
            fact_tokens=["FACT_US_BACKLOG_GROWTH_80", "FACT_ALABAMA_PLANT", "FACT_RATED_345KV", "FACT_ANTI_DUMPING_CLEAR"],
            irreplaceable_now="Only major Asian vendor with massive US backlog and anti-dumping clearance.",
            kill_switch="US DOE relaxes import ban on Chinese transformers.",
            market_share_proxy=8,
            expansion_speed_proxy=9
        ),
        CandidateCompany(
            company_name="Hyosung Heavy Industries",
            tickers=["298040.KS"],
            bottleneck_role="Secondary US Vendor",
            fact_tokens=["FACT_MEMPHIS_PLANT", "FACT_UK_GRID_DEAL", "FACT_UTILIZATION_100"],
            irreplaceable_now="Memphis plant operational; capacity overflow beneficiary.",
            kill_switch="Quality control failure in US plant.",
            market_share_proxy=7,
            expansion_speed_proxy=8
        ),
        CandidateCompany(
            company_name="LS Electric",
            tickers=["010120.KS"],
            bottleneck_role="Distribution Leader",
            fact_tokens=["FACT_DISTRIBUTION_LEADER", "FACT_BATTERY_PLANT_DEAL"],
            # Let's say for UHV Transformer specifically, they are catching up but maybe lacked certification locally in this mock context?
            # Or assume they pass but score lower.
            certification=True, 
            irreplaceable_now="Expanding into US market.",
            kill_switch="Failed US expansion.",
            market_share_proxy=5,
            expansion_speed_proxy=7
        ),
        CandidateCompany(
            company_name="Concept Power Co",
            tickers=["888888.KS"],
            bottleneck_role="New Entrant",
            fact_tokens=["FACT_PR_ONLY_ROADMAP"],
            revenue_exists=False,
            capacity_scale=False,
            delivery_record=False,
            leadtime_ok=True, # Theoretically
            irreplaceable_now="Planning to build factory.",
            kill_switch="Funding failure.",
            market_share_proxy=0
        )
    ],

    # Scenario 3: HBM Memory (Tech Phase Trigger)
    "HBM_STACKED_MEMORY": [
        CandidateCompany(
            company_name="SK Hynix",
            tickers=["000660.KS"],
            bottleneck_role="Sole Supplier (Initial)",
            fact_tokens=["FACT_NVIDIA_SUPPLIER", "FACT_SOLD_OUT_2024", "FACT_YIELD_LEADER_MR_MUF"],
            irreplaceable_now="Exclusive initial supplier for NVIDIA HBM3E.",
            kill_switch="Samsung Electronics successfully qualifies HBM3E with NVIDIA.",
            market_share_proxy=10,
            expansion_speed_proxy=8
        ),
        CandidateCompany(
            company_name="Samsung Electronics",
            tickers=["005930.KS"],
            bottleneck_role="Challenger",
            fact_tokens=["FACT_PR_ONLY_ROADMAP", "FACT_CAPACITY_HUGE"], # Has PR token
            # In this mock, Samsung fails the "Why Now" uniqueness or has PR_ONLY token for HBM3E specifically at this snapshot
            irreplaceable_now="Massive capacity waiting for qualification.",
            kill_switch="Fails qualification.",
            market_share_proxy=9, # High potential share, but...
            expansion_speed_proxy=9
        )
    ]
}
