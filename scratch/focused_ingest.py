import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

from src.ui.narratives.transcript_ingestor import ingest_transcript

vids = [
    "jYU7NkESKkE", "wyXybqB9ggI", "wl_JDcheBWc", "V3Pi86vfds0", 
    "c-UUPuaXYwA", "mksitWsvGBk", "WT2kVO-ZYi4", "KnziUrXipiY", 
    "eLmAlH2k-Ys", "WYkyN5DzYWw", "Ex_Em7cMybg", "fwOwPGfLph0", "hMW-cLS4y4A"
]

RAW_BASE = Path("data/raw/youtube")

for vid_id in vids:
    # Find metadata.json for this vid_id
    meta_paths = list(RAW_BASE.glob(f"**/**/**/{vid_id}/metadata.json"))
    if meta_paths:
        meta_path = meta_paths[0]
        print(f"Ingesting {vid_id} from {meta_path}...")
        ingest_transcript(meta_path)
    else:
        print(f"Metadata not found for {vid_id}")
