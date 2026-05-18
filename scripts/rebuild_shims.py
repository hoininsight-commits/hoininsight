import os
from pathlib import Path

UI_DIR = Path("src/ui")
UI_LOGIC_MAPPING = {
    "manifest_builder.py": "src.ui_logic.contracts.manifest_builder_v1",
    "operator_main_contract.py": "src.ui_logic.card_builders.operator_main_contract",
    "operator_narrative_order_builder.py": "src.ui_logic.ordering.operator_narrative_order_builder",
    "publish_ui_assets.py": "src.ui_logic.contracts.publish_ui_assets"
}

def rebuild_shims():
    for f_path in UI_DIR.glob("*.py"):
        if f_path.name == "__init__.py" or f_path.name.startswith("_"): continue
        
        name = f_path.name
        target = UI_LOGIC_MAPPING.get(name)
        
        if not target:
            stem = f_path.stem
            if stem.endswith("_narrator"):
                target = f"src.ui_logic.narrators.{stem}"
            elif stem.endswith("_detector") or stem.endswith("_exporter") or stem.endswith("_contract") or stem.endswith("_calendar") or stem.endswith("_renderer") or stem.endswith("_selector") or stem.endswith("_resolver") or stem.endswith("_generator"):
                target = f"src.ui_logic.card_builders.{stem}"
            elif "language_" in stem or "narrative_" in stem:
                target = f"src.ui_logic.narrators.{stem}"
            
        if target:
            content = f"from src.ui_logic.guards.legacy_usage_meter import hit_legacy\n"
            content += f"hit_legacy(__name__)\n"
            content += f"from {target} import *\n"
            
            f_path.write_text(content, encoding="utf-8")
            print(f"Rebuilt shim: {f_path.name} -> {target}")

if __name__ == "__main__":
    rebuild_shims()
