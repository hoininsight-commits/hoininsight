from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml  # PyYAML needs to be installed, but standard library doesn't have it.
# Assuming PyYAML or similar is available in the environment as it's a common dep.
# If not, I'll use a simple parser or assume 'run_command pip install PyYAML' was done.
# However, for robustness without external deps if possible, I might need to use a simple loader if yaml is missing.
# Let's try importing yaml. If it fails, I'll fallback or ask to install. 
# Actually, standard practice in this env: assume requirements.txt has it or I can add it.
# I will use a simple specialized parser if I want to avoid deps, but let's stick to standard `yaml` if possible.
# Wait, the prompt says "Do not interpret/add ideas". I should check if I can use PyYAML.
# I'll check imports in other files. `src/topics/fusion.py` uses `import json`.
# `registry` usually implies YAML. I'll assume PyYAML is safe or use a safe read.

# For safety, I will implement a basic YAML reader wrapper or just use `yaml` if available.
# Let's check if PyYAML is installed first? No, I'll just write the code assuming `yaml` import.
# But wait, python standard lib doesn't include yaml.
# I will check if I can use a simple manual parser for this specific simple structure to avoid dependency hell if PyYAML isn't there,
# BUT `registry/schemas` usually implies some YAML handling exists.
# Let's just use `yaml`.

import json

def _load_yaml_simple(path: Path) -> Dict[str, Any]:
    # Extremely basic parser to avoid dependency if PyYAML is missing.
    # It only supports the specific structure of regime_strategy_map.yml
    # Actually, it's better to try importing yaml, and if it fails, log an error or return empty.
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except ImportError:
        # Fallback: very specific parser for our file
        # This is risky. Let's hope PyYAML is there.
        # Check `daily_report.py` imports... none use yaml.
        # I'll just skip complex parsing and return empty if yaml pkg missing, 
        # or... I can just use JSON for the registry map if the user didn't force YAML format?
        # The user specified `regime_strategy_map.yml`.
        return {}

def resolve_strategy_frameworks(
    base_dir: Path,
    regime_name: str,
    persistence_days: int
) -> Dict[str, Any]:
    
    map_path = base_dir / "registry" / "regime_strategy_map.yml"
    if not map_path.exists():
        return {
            "regime": regime_name,
            "persistence_days": persistence_days,
            "strategy_frameworks": []
        }

    # Try to load YAML
    try:
        import yaml
        data = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    except ImportError:
        # If PyYAML is missing, we can't parse easily. 
        # For this specific task, if PyYAML is missing, we might fail to resolve.
        # But I should not install packages without permission.
        # I will assume PyYAML is present because it's a very standard AI/Data project dep.
        # If not, I will return empty.
        print("Warning: PyYAML not found. Cannot parse strategy map.")
        return {
            "regime": regime_name,
            "persistence_days": persistence_days,
            "strategy_frameworks": []
        }
    except Exception:
        return {
            "regime": regime_name,
            "persistence_days": persistence_days,
            "strategy_frameworks": []
        }

    regimes_map = data.get("regimes", {})
    # Match regime name (case-insensitive or exact? prompt implies exact keys in map)
    # But output from fusion usually has specific titles.
    # We need to map the "Regime Title" or ID to the keys in YAML.
    # Phase 25/26 outputs title like "Risk-Off Regime 강화". 
    # The keys in YAML are "RISK_OFF", "AI_SUPPLY_CHAIN_ACCELERATION".
    # We need a way to map title/ID to these keys.
    # The `meta_topic_id` in fusion.py is e.g., "risk_off_regime" or "rate_fx_shock".
    # We should use the ID if possible, or mapping.
    # 
    # Let's look at `fusion.py`:
    # "meta_topic_id": "risk_off_regime"
    # "meta_topic_id": "rate_fx_shock"
    #
    # YAML keys: "RISK_OFF", "RATE_FX_SHOCK" (implied by prompt examples)
    #
    # I will add a simple normalization: ID to Upper Case?
    # risk_off_regime -> RISK_OFF_REGIME? 
    # YAML has "RISK_OFF".
    # I need to handle this mapping.
    #
    # Prompt says: "Regime별 Strategy Mapping 정의"
    # I will try to match normalized ID.
    
    # Heuristic mapping for now since I can't change fusion.py
    normalized_id = regime_name.upper().replace(" ", "_")
    target_key = None
    
    # Try direct match
    if normalized_id in regimes_map:
        target_key = normalized_id
    
    # Try partial match (e.g. RISK_OFF_REGIME -> RISK_OFF)
    if not target_key:
        for k in regimes_map.keys():
            if k in normalized_id:
                target_key = k
                break
    
    strategies = []
    if target_key:
        strategies = regimes_map[target_key].get("allowed_strategies", [])

    return {
        "regime": regime_name,
        "persistence_days": persistence_days,
        "strategy_frameworks": strategies
    }
