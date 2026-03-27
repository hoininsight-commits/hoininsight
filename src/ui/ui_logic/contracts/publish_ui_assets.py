import shutil
import os
import json
from datetime import datetime
from pathlib import Path

def publish_assets(project_root: Path):
    """
    Synchronizes data/ui/ and data/decision/ to docs/data/ui/ and docs/data/decision/.
    Ensures docs/data/ targets only.
    """
    src_ui = project_root / "data" / "ui"
    src_decision = project_root / "data" / "decision"
    
    dest_base = project_root / "docs" / "data"
    dest_outputs = project_root / "data_outputs"
    
    # Standard docs/ targets
    dest_ui = dest_base / "ui"
    dest_decision = dest_base / "decision"
    
    # Enhanced data_outputs/ targets
    out_ui = dest_outputs / "ui"
    out_decision = dest_outputs / "decision"
    
    # Ensure manifest exists before publishing
    manifest_file = src_ui / "manifest.json"
    if not manifest_file.exists():
        print("[Publish] Manifest missing. Triggering ManifestBuilder...")
        # Redirect to new standard path
        try:
            from src.ui.ui_logic.contracts.manifest_builder_v3 import build_manifest_v3 as build_m
        except ImportError:
            from src.ui.manifest_builder import build_manifest as build_m
        build_m(project_root)
        

    # ADD-ONLY Transformation Layer (Phase 5)
    def transform_decision_card(item_key, item_data):
        """
        Enriches raw interpretation units with UI-contract fields.
        Does NOT modify original source, only the output copy.
        """
        # 1. Title Generation
        if "title" not in item_data:
            narrative = item_data.get("structural_narrative", "")
            target = item_data.get("target_sector", "Unknown")
            # Use narrative head or target + key
            item_data["title"] = f"[{target}] {narrative[:30]}..." if narrative else f"[{target}] Signal Detected"

        # 2. Selected At (Synthesis)
        if "selected_at" not in item_data:
            # Default to 09:00 AM of as_of_date if missing
            date_str = item_data.get("as_of_date", "2026-01-01")
            item_data["selected_at"] = f"{date_str}T09:00:00"

        # 3. Date normalization
        if "date" not in item_data:
            item_data["date"] = item_data.get("as_of_date", "2026-01-01")

        # 4. Intensity (Score Normalization)
        if "intensity" not in item_data:
            # Map 0.0-1.0 to 0-100
            score = item_data.get("confidence_score", 0.5)
            # Handle string case if any
            try:
                item_data["intensity"] = int(float(score) * 100)
            except:
                item_data["intensity"] = 50

        # 5. Speakability (Placeholder if missing)
        if "speakability" not in item_data:
            item_data["speakability"] = "Review Required"

        # 6. Why Now Summary
        if "why_now_summary" not in item_data:
            item_data["why_now_summary"] = item_data.get("structural_narrative", "No narrative available.")

        # 7. Anomaly Points
        if "anomaly_points" not in item_data:
            item_data["anomaly_points"] = item_data.get("evidence_tags", [])

        # 8. Related Assets
        if "related_assets" not in item_data:
            item_data["related_assets"] = item_data.get("evidence_refs", [])

        # 9. Content Hook
        if "content_hook" not in item_data:
            item_data["content_hook"] = item_data.get("structural_narrative", "")

        return item_data


    def sync_dir(src: Path, dest: Path, transform=False):
        if not src.exists():
            print(f"[Publish] Source {src} does not exist. Skipping.")
            return
        
        dest.mkdir(parents=True, exist_ok=True)
        # Use rglob for recursive discovery (Phase 13.1 Fix)
        for item in src.rglob("*"):
            if item.is_file():
                # Determine target path relative to src
                rel_path = item.relative_to(src)
                target_path = dest / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Read-Transform-Write flow for decision files
                if transform and item.suffix == ".json" and "decision" in str(src):
                    try:
                        with open(item, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        
                        # Handle list or dict
                        if isinstance(data, list):
                            new_data = [transform_decision_card(i, x) for i, x in enumerate(data)]
                        elif isinstance(data, dict):
                            # Try to detect if it's a map of id->card or just a card
                            is_map = all(isinstance(v, dict) for v in data.values())
                            if is_map:
                                new_data = {k: transform_decision_card(k, v) for k, v in data.items()}
                            else:
                                new_data = transform_decision_card("root", data)
                        else:
                            new_data = data

                        with open(target_path, "w", encoding="utf-8") as f:
                            json.dump(new_data, f, indent=2, ensure_ascii=False)
                        print(f"[Publish] Transformed & Copied {rel_path}")
                        continue
                    except Exception as e:
                        print(f"[Publish] Transform failed for {item.name}: {e}. Falling back to raw copy.")

                shutil.copy2(item, target_path)
                print(f"[Publish] Copied {rel_path} to {dest}")

    print("\n[Publish] Synchronizing UI assets...")
    sync_dir(src_ui, dest_ui, transform=False)
    sync_dir(src_ui, out_ui, transform=False)
    

    print("\n[Publish] Synchronizing Decision assets (Recursive)...")
    sync_dir(src_decision, dest_decision, transform=True)
    sync_dir(src_decision, out_decision, transform=True)
    
    # [FIX] Generate Deep Decision Manifest for Navigator
    # Allows UI to discover all decision files in dated subfolders
    raw_files = list(dest_decision.rglob("*.json"))
    decision_files = []
    for rf in raw_files:
        if rf.name == "manifest.json": continue
        # Get path relative to docs/data/decision
        rel_path = rf.relative_to(dest_decision)
        decision_files.append(str(rel_path))

    manifest = {
        "generated_at": datetime.now().isoformat(),
        "files": sorted(decision_files, reverse=True) # Newest first
    }
    with open(dest_decision / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[Publish] Generated recursive manifest with {len(decision_files)} entries.")

    with open(out_decision / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    
    # NEW: Publish OPS data for System Status View
    src_ops = project_root / "data" / "ops"
    dest_ops = dest_base / "ops"
    out_ops = dest_outputs / "ops"
    
    if src_ops.exists():
        print("\n[Publish] Synchronizing Ops assets...")
        dest_ops.mkdir(parents=True, exist_ok=True)
        out_ops.mkdir(parents=True, exist_ok=True)
        
        # 1. Standard Ops Packs (Transferred via Authority List)
        ops_packs = [
            "video_candidate_pool.json",
            "video_script_pack.json",
            "video_script_pack.md",
            "stock_linkage_pack.json",
            "conflict_density_pack.json",
            "regime_state.json",
            "investment_os_state.json",
            "investment_os_brief.md",
            "capital_allocation_state.json",
            "capital_allocation_brief.md",
            "timing_state.json",
            "timing_brief.md",
            "probability_compression_state.json",
            "probability_compression_brief.md",
            "meta_volatility_state.json",
            "meta_volatility_brief.md",
            "phase15_detection_diagnostics.md",
            "phase15_conflict_trace.md",
            "economic_hunter_radar.json",
            "topic_probability_ranking.json",
            "usage_audit.json",
            "system_health.json",
            # STEP-52: Core Narrative Lock Engine Outputs
            "top_topic.json",
            "script_output.json",
            "mentionables.json",
            "today_operator_brief.json",
            "core_theme_state.json"
        ]
        
        for pack in ops_packs:
            s_file = src_ops / pack
            if s_file.exists():
                shutil.copy2(s_file, dest_ops / pack)
                shutil.copy2(s_file, out_ops / pack)
                print(f"✅ [OK] {pack}")

        # [STEP-52] Synchronize Operator folder to docs/data/operator
        src_operator = project_root / "data" / "operator"
        dest_operator = dest_base / "operator"
        if src_operator.exists():
            dest_operator.mkdir(parents=True, exist_ok=True)
            for item in src_operator.glob("*.json"):
                shutil.copy2(item, dest_operator / item.name)
                print(f"✅ [OPERATOR] {item.name}")

        # [STEP-52] Specific verification folders
        mapping = {
            "topic": "top_topic.json",
            "content": "script_output.json",
            "impact": "mentionables.json"
        }
        for folder, filename in mapping.items():
            s_file = src_ops / filename
            d_dir = dest_base / folder
            if s_file.exists():
                d_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(s_file, d_dir / filename)
                print(f"✅ [VERIFY-SYNC] {folder}/{filename}")

        # 2. System Health - now generated by src.ops.system_health_generator
        pass
    
    print("\n[Publish] Sync completed to docs/data/* and data_outputs/*")


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent.parent.parent
    publish_assets(project_root)

