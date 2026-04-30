
import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

from src.ui.narratives.transcript_ingestor import ingest_transcript

vids = [
    "FD8Tjeqz740", "Aleb9BDprHM", "IQISANNisek", "XfQWDjRqIFI",
    "dauij0Vh9nQ", "GBqse9oamvM", "rj9x30sqzww", "2XGjXaDRno0",
    "uiq5EwMjxwA", "dxTiv8OFacw", "7CK2cnKcEMs", "e9nlgvRTLt8", "B72o1tKOHYY"
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
