import os
import ssl
import json
import logging
import yaml
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("YouTubeWatcher")

REGISTRY_PATH = Path("registry/narrative_sources.yml")
DATA_DIR = Path("data/narratives/raw/youtube")

def _utc_from_iso(iso_str: str) -> str:
    """Standardize timestamp to UTC string."""
    try:
        # YouTube RSS usually returns ISO format like 2024-01-15T10:00:00+00:00
        # Just ensure it's clean string
        return iso_str
    except:
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _utc_date_parts(iso_str: str) -> tuple[str, str, str]:
    """Extract YYYY, MM, DD from ISO timestamp."""
    # Simple parse, assuming ISO format
    # 2024-01-15T... -> 2024, 01, 15
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        return dt.strftime("%Y"), dt.strftime("%m"), dt.strftime("%d")
    except:
        now = datetime.utcnow()
        return now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")

def fetch_rss_feed(channel_id: str) -> str:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        req = Request(url, headers={"User-Agent": "hoin-insight-watcher/1.0"})
        # Allow legacy SSL if needed (macOS python issue workaround)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urlopen(req, context=ctx, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        logger.error(f"RSS Fetch Failed for {channel_id}: {e}")
        return ""

def parse_feed_entries(xml_content: str):
    if not xml_content:
        return []
    
    entries = []
    try:
        root = ET.fromstring(xml_content)
        # Namespace map might be needed
        ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 
              'media': 'http://search.yahoo.com/mrss/', 
              'atom': 'http://www.w3.org/2005/Atom'}
        
        # ET uses {uri}tag syntax if not using find with namespaces dict fully
        # Simple iteration is often easier
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            vid_id_tag = entry.find("{http://www.youtube.com/xml/schemas/2015}videoId")
            vid_id = vid_id_tag.text if vid_id_tag is not None else None
            
            title_tag = entry.find("{http://www.w3.org/2005/Atom}title")
            title = title_tag.text if title_tag is not None else "No Title"
            
            pub_tag = entry.find("{http://www.w3.org/2005/Atom}published")
            published = pub_tag.text if pub_tag is not None else ""
            
            link_tag = entry.find("{http://www.w3.org/2005/Atom}link")
            link = link_tag.attrib.get('href') if link_tag is not None else ""
            
            author_tag = entry.find("{http://www.w3.org/2005/Atom}author")
            author_name = "Unknown"
            if author_tag is not None:
                name_tag = author_tag.find("{http://www.w3.org/2005/Atom}name")
                if name_tag is not None:
                    author_name = name_tag.text

            if vid_id:
                entries.append({
                    "id": vid_id,
                    "title": title,
                    "published_at": _utc_from_iso(published),
                    "url": link,
                    "channel_name": author_name
                })
    except Exception as e:
        logger.error(f"XML Parse Error: {e}")
        
    return entries

def run_watcher():
    if not REGISTRY_PATH.exists():
        logger.warning(f"Registry not found at {REGISTRY_PATH}")
        return

    try:
        config = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to load registry: {e}")
        return

    sources = config.get("sources", [])
    new_count = 0
    new_titles = []

    for src in sources:
        if not src.get("enabled", False):
            continue
        
        sid = src.get("source_id")
        cid = src.get("channel_id")
        logger.info(f"Checking Source: {src.get('name')} ({sid})")
        
        xml_data = fetch_rss_feed(cid)
        entries = parse_feed_entries(xml_data)
        
        for vid in entries:
            vid_id = vid["id"]
            y, m, d = _utc_date_parts(vid["published_at"])
            
            save_dir = DATA_DIR / y / m / d / vid_id
            meta_path = save_dir / "metadata.json"
            
            if meta_path.exists():
                logger.debug(f"Video already exists: {vid_id} - {vid['title']}")
                continue
            
            # Save New Video Metadata
            try:
                save_dir.mkdir(parents=True, exist_ok=True)
                
                payload = {
                    "video_id": vid_id,
                    "source_id": sid,
                    "title": vid["title"],
                    "published_at": vid["published_at"],
                    "url": vid["url"],
                    "channel_name": vid["channel_name"],
                    "collected_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                }
                
                meta_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                logger.info(f"[NEW] Detected: {vid['title']}")
                new_count += 1
                new_titles.append(vid["title"])
            except Exception as e:
                logger.error(f"Failed to save metadata for {vid_id}: {e}")

    # Export new titles for notifications
    if new_titles:
        try:
            status_dir = Path("data/narratives/status")
            status_dir.mkdir(parents=True, exist_ok=True)
            (status_dir / "recent_new_titles.txt").write_text("\n".join(new_titles), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to export new titles: {e}")

    logger.info(f"Watcher Complete. New Videos: {new_count}")

if __name__ == "__main__":
    run_watcher()
