import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

class ContentPackMultiPackLayer:
    """
    IS-98-2a: Multi-Pack Layer
    Bundles daily content into a 1 Long + 4 Shorts format using deterministic selection.
    """

    def __init__(self, output_dir: str = "data/decision"):
        self.output_dir = Path(output_dir)

    def run(self, packs: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not packs:
            return self._empty_result("No packs available")

        # 1. Scoring & Sorting
        scored_candidates = []
        for pack in packs:
            score = self._calculate_score(pack)
            scored_candidates.append({"score": score, "pack": pack})

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        # 2. Partitioning: 1 Long + 4 Shorts
        long_pack = None
        short_packs = []
        
        # Try to find a valid Long pack
        for i, item in enumerate(scored_candidates):
            p = item["pack"]
            # Prerequisite: READY and (3+ citations or 2+ mentionables)
            cites = len(p["assets"].get("evidence_sources", []))
            mentions = len(p["assets"].get("mentionables", []))
            
            if p["status"]["speakability"] == "READY" and (cites >= 3 or mentions >= 2):
                long_pack = self._transform_to_format(p, "LONG")
                # Remove selected from list
                scored_candidates.pop(i)
                break
        
        # Fallback for Long: If no READY Long found, take absolute top one as Long (if READY)
        if not long_pack and scored_candidates:
            if scored_candidates[0]["pack"]["status"]["speakability"] == "READY":
                long_pack = self._transform_to_format(scored_candidates[0]["pack"], "LONG")
                scored_candidates.pop(0)

        # Collect up to 4 Shorts (READY or Promoted HOLD)
        for item in scored_candidates:
            if len(short_packs) >= 4:
                break
            p = item["pack"]
            if p["status"]["speakability"] == "READY":
                short_packs.append(self._transform_to_format(p, "SHORT"))
            elif p["status"]["speakability"] == "HOLD":
                if self._check_promotion(p):
                    short_packs.append(self._transform_to_format(p, "SHORT", promoted=True))

        # 3. Final Assembly
        all_packs = []
        if long_pack:
            all_packs.append(long_pack)
        all_packs.extend(short_packs)

        for i, p in enumerate(all_packs):
            p["pack_id"] = f"{p['format']}_{today_id}_{i+1:03d}"

        result = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "packs": all_packs,
            "summary": {
                "long_count": 1 if long_pack else 0,
                "short_count": len(short_packs),
                "ready_count": sum(1 for p in packs if p["status"]["speakability"] == "READY"),
                "hold_included": sum(1 for p in short_packs if p.get("promoted"))
            },
            "governance": {
                "deterministic": True,
                "no_llm": True,
                "add_only_integrity": True
            }
        }
        return result

    def _calculate_score(self, pack: Dict) -> int:
        score = 0
        status = pack["status"]["speakability"]
        if status == "READY":
            score += 100
        
        # +1 per verified citation
        citations = pack["assets"].get("evidence_sources", [])
        score += sum(1 for c in citations if c.get("status") == "VERIFIED")
        
        # +10 for mentionables
        if pack["assets"].get("mentionables"):
            score += 10
        
        # +20 for complexity (dummy check for now, can be interpretation unit count in real scenario)
        # If the pack came from IS-98-2, we assume it's already a link.
        return score

    def _check_promotion(self, pack: Dict) -> bool:
        # Promote HOLD if high-impact keywords present in title or why_now
        keywords = ["발표", "출시", "확정", "합의", "타결"]
        text = str(pack["assets"].get("title", "")) + str(pack["assets"]["decision_card"].get("why_now", ""))
        has_keyword = any(kw in text for kw in keywords)
        
        # Must have at least PARTIAL or VERIFIED citation
        has_cite = any(c.get("status") in ["VERIFIED", "PARTIAL"] for c in pack["assets"].get("evidence_sources", []))
        
        return has_keyword and has_cite

    def _transform_to_format(self, pack: Dict, fmt: str, promoted: bool = False) -> Dict:
        new_pack = pack.copy()
        new_pack["format"] = fmt
        if promoted:
            new_pack["promoted"] = True
            new_pack["status"]["speakability"] = "READY (PROMOTED)"
        
        # In IS-98-2, the script already contains both shorts and long blocks.
        # We just clean up or set a flag.
        if fmt == "SHORT":
            # For SHORT format, we only keep shorts_script in the primary script view
            new_pack["script"] = pack["assets"]["shorts_script"]
        else:
            # For LONG format, we keep long_script
            new_pack["script"] = pack["assets"]["long_script"]
            
        return new_pack

    def _empty_result(self, reason: str) -> Dict:
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "packs": [],
            "summary": {"reason": reason},
            "governance": {"deterministic": True}
        }

    def save(self, data: Dict[str, Any], filename: str = "content_pack_multipack.json"):
        p = self.output_dir / filename
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Saved Multi-Pack to {p}")

today_id = datetime.now().strftime("%Y%m%d")

def run_multipack_layer(data_dir: str = "data/decision"):
    base = Path(data_dir)
    pack_file = base / "content_pack.json"
    if not pack_file.exists():
        print(f"[ERROR] {pack_file} not found.")
        return None
    
    packs = json.loads(pack_file.read_text(encoding="utf-8"))
    layer = ContentPackMultiPackLayer(output_dir=str(base))
    result = layer.run(packs)
    layer.save(result)
    return result
