# Phase 31-A Implementation Plan: YouTube Watcher & Transcript Ingestion

## Goal
Automate the detection and ingestion of new video content from designated YouTube channels ("Narrative Sources") to build a "Narrative Raw Data" repository.
Critically, this phase performs **Collection Only**. No interpretation, summarization, or analysis.

## User Review Required
- **None**: Technical implementation of data collection.

## Proposed Changes

### Registry
#### [NEW] [registry/narrative_sources.yml](file:///Users/jihopa/.gemini/antigravity/scratch/HoinInsight/registry/narrative_sources.yml)
- Define `youtube_economic_hunter` (경제사냥꾼) as the initial source.
- Channel ID: `UC7usMJDHmtbs_oegmzQKKMA`
- Configurable `update_check` frequency.

### Logic Layer (Narratives)
#### [NEW] [src/narratives/youtube_watcher.py](file:///Users/jihopa/.gemini/antigravity/scratch/HoinInsight/src/narratives/youtube_watcher.py)
- **Role**: Detect new videos.
- **Method**: Use Channel RSS Feed (`https://www.youtube.com/feeds/videos.xml?channel_id=...`) for robust, reliable, and free detection of new uploads.
- **Output**: `data/narratives/raw/youtube/YYYY/MM/DD/<video_id>/metadata.json`
- **Fields**: `id`, `title`, `published_at`, `url`, `channel`.

#### [NEW] [src/narratives/transcript_ingestor.py](file:///Users/jihopa/.gemini/antigravity/scratch/HoinInsight/src/narratives/transcript_ingestor.py)
- **Role**: Download text content.
- **Dependencies**: `youtube-transcript-api`.
- **Logic**:
    1. Check for valid video metadata in `data/narratives/raw/youtube`.
    2. Try fetching captions (KR/EN).
    3. If fails, fetch description.
    4. Save to `data/narratives/transcripts/...`.

#### [NEW] [src/narratives/narrative_status.py](file:///Users/jihopa/.gemini/antigravity/scratch/HoinInsight/src/narratives/narrative_status.py)
- **Role**: Record execution metrics.
- **Output**: `data/narratives/status/YYYY/MM/DD/collection_status.json`.

### CI/CD
#### [MODIFY] [.github/workflows/full_pipeline.yml](file:///Users/jihopa/.gemini/antigravity/scratch/HoinInsight/.github/workflows/full_pipeline.yml)
- **New Step**: `Run Narrative Watcher (Phase 31-A)`
- **New Verify**: `Verify Phase 31-A Narrative Ingestion` checks for status file.

### Dependencies
#### [MODIFY] [pyproject.toml](file:///Users/jihopa/.gemini/antigravity/scratch/HoinInsight/pyproject.toml)
- Add `youtube-transcript-api`. (For robust caption retrieval without API key).
- Add `feedparser` (Optional, but robust for RSS. If not, simple XML parsing works). I will use `xml.etree.ElementTree` to keep dependencies low if possible, or just regex if really simple. RSS XML is simple.

## Verification Plan
1. **Source Discovery**: Confirm "경제사냥꾼" Channel ID.
2. **Local Run**: Execute `python -m src.narratives.youtube_watcher` and `transcript_ingestor`.
3.  **Check Artifacts**: Verify files in `data/narratives/raw` and `data/narratives/transcripts`.
4.  **Pipeline**: Push and verify CI run.
