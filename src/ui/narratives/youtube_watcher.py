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
from src.utils.target_date import get_now_kst, get_target_ymd

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("YouTubeWatcher")

from src.utils.guards import check_learning_enabled
from src.ui.narratives.transcript_ingestor import ingest_transcript
from src.utils.telegram_notifier import TelegramNotifier

REGISTRY_PATH = Path("registry/narrative_sources.yml")
DATA_DIR = Path("youtube_data/raw")

def _utc_from_iso(iso_str: str) -> str:
    """Standardize timestamp to UTC string."""
    try:
        # YouTube RSS usually returns ISO format like 2024-01-15T10:00:00+00:00
        # Just ensure it's clean string
        return iso_str
    except:
        return get_now_kst().strftime("%Y-%m-%dT%H:%M:%SZ")

def _utc_date_parts(iso_str: str) -> tuple[str, str, str]:
    """Extract YYYY, MM, DD from ISO timestamp."""
    # Simple parse, assuming ISO format
    # 2024-01-15T... -> 2024, 01, 15
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        return dt.strftime("%Y"), dt.strftime("%m"), dt.strftime("%d")
    except:
        now = get_now_kst()
        return now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")

def fetch_rss_feed(channel_id: str) -> str:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        # Use a simpler User-Agent that worked in testing
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=30)
        
        # If we have a body that looks like a feed, return it regardless of status code
        if "<feed" in resp.text and "<entry" in resp.text:
            return resp.text
            
        if resp.status_code == 200:
            return resp.text
            
        logger.error(f"RSS Fetch Failed for {channel_id}: Status {resp.status_code}")
        return ""
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

def is_youtube_shorts(video_id: str) -> bool:
    """Checks if a video is a YouTube Short by checking the redirect behavior."""
    try:
        import requests
        url = f"https://www.youtube.com/shorts/{video_id}"
        # allow_redirects=False로 설정하여 리다이렉트가 발생하는지 확인
        response = requests.head(url, allow_redirects=False, timeout=5)
        # 쇼츠면 200 OK, 일반 영상이면 303/302 리다이렉트 발생
        return response.status_code == 200
    except Exception:
        return False

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
            transcript_dir = Path("youtube_data/transcripts") / y / m / d
            transcript_path = transcript_dir / file_name
            legacy_txt_path = transcript_dir / f"{vid_id}.txt"
            meta_path = save_dir / "metadata.json"
            
            # 1. 파일명 정규화 (이미 VideoID.txt로 있는 경우 이름 변경)
            if legacy_txt_path.exists() and not transcript_path.exists():
                logger.info(f"Renaming legacy transcript: {vid_id}.txt -> {file_name}")
                transcript_dir.mkdir(parents=True, exist_ok=True)
                legacy_txt_path.rename(transcript_path)

            # 2. 메타데이터 저장 (없을 경우에만)
            if not meta_path.exists():
                try:
                    save_dir.mkdir(parents=True, exist_ok=True)
                    payload = {
                        "video_id": vid_id,
                        "source_id": sid,
                        "title": vid["title"],
                        "published_at": vid["published_at"],
                        "url": vid["url"],
                        "channel_name": vid["channel_name"],
                        "collected_at": get_now_kst().strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                    meta_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                    logger.info(f"[NEW] Metadata saved: {vid['title']}")
                    new_count += 1
                    new_titles.append(vid["title"])
                except Exception as e:
                    logger.error(f"Failed to save metadata for {vid_id}: {e}")
                    continue

            # 3. 자막 수집 및 알림 (자막 파일이 없을 경우에만 실행)
            if not transcript_path.exists():
                logger.info(f"Transcript missing. Triggering ingestion for: {vid_id}...")
                try:
                    # 자막 수집 시도
                    ingest_transcript(meta_path)
                    
                    # 수집 후 파일이 생성되었는지 확인 (ingest_transcript는 VideoID.txt로 저장함)
                    if legacy_txt_path.exists():
                        # 이름 변경 (규칙 적용)
                        transcript_dir.mkdir(parents=True, exist_ok=True)
                        legacy_txt_path.rename(transcript_path)
                        
                        # [v19.5] 수집 성공 시 텔레그램 발송
                        script_content = transcript_path.read_text(encoding="utf-8")
                        
                        # 요약 생성
                        # 요약 생성 스킵 (스크립트만 수집)
                        summary = ""

                        # [v20.0] 쇼츠 여부 판별
                        is_shorts = is_youtube_shorts(vid_id)
                        type_tag = "🎬 *[유튜브 쇼츠]*" if is_shorts else "📺 *[유튜브 일반 영상]*"

                        msg = f"{type_tag}\n\n"
                        msg += f"📌 *제목*: {vid['title']}\n"
                        msg += f"⏰ *회차*: {run_round}회차\n"
                        msg += f"🔗 [영상 링크]({vid['url']})\n\n"
                        
                        if summary:
                            msg += f"💡 *핵심 요약*:\n{summary}\n\n"
                            msg += f"------------------\n\n"
                        
                        msg += f"📜 *스크립트 전문*:\n{script_content}"
                        
                        notifier = TelegramNotifier(target="TRANSCRIPT")
                        notifier.send_message_in_chunks(msg)
                        logger.info(f"Telegram notification sent for {vid_id}")
                except Exception as ingest_e:
                    logger.error(f"Failed to ingest transcript for {vid_id}: {ingest_e}")

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
