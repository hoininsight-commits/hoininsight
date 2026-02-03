"""
Daily Content Pack Pipeline Runner (IS-99-2)
Orchestrates the sequence of deterministic layers to produce final operational exports.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.decision.run_is96_4 import main as run_is96_4
from src.engine.content.content_speak_map import run_content_speak_map
from src.topics.narrator.script_realization import run_script_realization
from src.topics.narrator.tone_persona_lock import run_tone_persona_lock
from src.topics.mentionables.mentionables_layer import run_mentionables_layer
from src.topics.citations.evidence_citation_layer import run_citation_layer
from src.topics.content_pack.content_pack_layer import run_content_pack_layer
from src.topics.content_pack.content_pack_multipack_layer import run_multipack_layer
from src.topics.content_pack.daily_run_orchestrator import run_orchestrator as run_final_export

def main():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> STARTING CONTENT PACK PIPELINE (IS-99-2)")
    
    try:
        # 1. Decision Assembly (Interpretation + Speakability + Skeleton)
        print("\n[Step 1/9] Running Decision Assembly (IS-96)...")
        run_is96_4()

        # 2. Content Speak Map
        print("\n[Step 2/9] Running Content Speak Map (IS-97)...")
        run_content_speak_map()
        
        # 3. Script Realization
        print("\n[Step 3/9] Running Script Realization (IS-97)...")
        run_script_realization()
        
        # 4. Tone & Persona Lock
        print("\n[Step 4/9] Running Tone & Persona Lock (IS-97)...")
        run_tone_persona_lock()
        
        # 5. Mentionables
        print("\n[Step 5/9] Running Mentionables Layer (IS-97)...")
        run_mentionables_layer()
        
        # 6. Evidence Citations
        print("\n[Step 6/9] Running Evidence Citation Layer (IS-98)...")
        run_citation_layer()
        
        # 7. Content Pack Aggregation
        print("\n[Step 7/9] Running Content Pack Layer (IS-98)...")
        run_content_pack_layer()
        
        # 8. Multi-Pack Bundling
        print("\n[Step 8/9] Running Multi-Pack Layer (IS-98a)...")
        run_multipack_layer()
        
        # 9. Final Orchestration (Exports)
        print("\n[Step 9/9] Running Daily Run Orchestrator (IS-99)...")
        run_final_export()
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] <<< CONTENT PACK PIPELINE COMPLETED SUCCESSFULLY")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
