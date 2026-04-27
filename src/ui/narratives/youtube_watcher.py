import os
import ssl
import json
import logging
import yaml
import requests
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("YouTubeWatcher")

from src.utils.guards import check_learning_enabled
from src.ui.narratives.transcript_ingestor import ingest_transcript
from src.utils.telegram_notifier import TelegramNotifier

REGISTRY_PATH = Path("registry/narrative_sources.yml")
DATA_DIR = Path("data/raw/youtube")

def _utc_from_iso(iso_str: str) -> str:
    """Standardize timestamp to UTC string."""
    try:
        # YouTube RSS usually returns ISO format like 2024-01-15T10:00:00+00:00
        # Just ensure it's clean string
        return iso_str
    except:
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

def _utc_date_parts(iso_str: str) -> tuple[str, str, str]:
    """Extract YYYY, MM, DD from ISO timestamp."""
    # Simple parse, assuming ISO format
    # 2024-01-15T... -> 2024, 01, 15
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        return dt.strftime("%Y"), dt.strftime("%m"), dt.strftime("%d")
    except:
        now = datetime.now()
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
                author_name_tag = author_tag.find("{http://www.w3.org/2005/Atom}name")
                if author_name_tag is not None:
                    author_name = author_name_tag.text

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

def run_watcher(run_round: int = 1):
    # Metadata collection from RSS is always allowed to keep index fresh.
    # Learning guard applies to heavy processing/LLM phases.
    learning_enabled = os.environ.get("ENABLE_LEARNING", "false").lower() == "true" or \
                       os.environ.get("SKIP_GUARD", "false").lower() == "true"
    
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
            
            # [CUSTOM RULE] 날짜_회차_제목.txt 형식의 파일명 생성
            safe_title = re.sub(r'[\\/*?:"<>|]', "", vid["title"]).replace(" ", "_")
            file_name = f"{y}{m}{d}_{run_round}회차_{safe_title}.txt"
            transcript_path = Path("data/transcripts/youtube") / y / m / d / file_name
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
                    "collected_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                }
                
                meta_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                logger.info(f"[NEW] Detected: {vid['title']}")
                new_count += 1
                new_titles.append(vid["title"])
                
                # Fetch transcript immediately after saving metadata
                logger.info(f"Triggering transcript ingestion for: {vid_id}...")
                try:
                    # ingest_transcript가 특정 경로에 저장할 수 있도록 옵션이 필요할 수 있으나, 
                    # 여기서는 수집 후 텔레그램 발송에 집중
                    ingest_transcript(meta_path)
                    
                    # 수집 성공 시 텔레그램 발송 (v17.5 New Requirement)
                    # 실제 자막 파일 위치 확인
                    actual_txt_path = Path("data/transcripts/youtube") / y / m / d / f"{vid_id}.txt"
                    if actual_txt_path.exists():
                        # 파일 이름 변경 (사용자 요청 규칙)
                        transcript_path.parent.mkdir(parents=True, exist_ok=True)
                        actual_txt_path.rename(transcript_path)
                        
                        script_content = transcript_path.read_text(encoding="utf-8")
                        msg = f"📺 *[유튜브 수집 완료]*\n\n"
                        msg += f"📌 *제목*: {vid['title']}\n"
                        msg += f"⏰ *회차*: {run_round}회차\n"
                        msg += f"🔗 [영상 링크]({vid['url']})\n\n"
                        msg += f"📜 *스크립트 전문*:\n{script_content}"
                        
                        notifier = TelegramNotifier()
                        notifier.send_message_in_chunks(msg)
                        logger.info(f"Telegram notification sent for {vid_id}")

                except Exception as ingest_e:
                    logger.error(f"Failed to ingest transcript right away for {vid_id}: {ingest_e}")
                    
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
