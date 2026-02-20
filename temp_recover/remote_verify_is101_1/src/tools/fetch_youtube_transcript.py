
from playwright.sync_api import sync_playwright
import time
import sys

def fetch_transcript(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Navigating to {url}...")
        page.goto(url)
        time.sleep(5)  # Wait for load
        
        try:
            # Click 'Expand description'
            # Note: Selectors on YouTube change often. This is a best effort.
            # Using 'More' button in description
            # Actually, simpler to just grab title first
            title = page.title()
            print(f"Title: {title}")
            
            # For shorts, the UI is different. 
            # Let's try to grab the structured data or description if possible. 
            # Or use a dedicated library in python if available.
            # But wait, youtube-transcript-api is the standard.
            # The previous error was `AttributeError: type object 'YouTubeTranscriptApi' has no attribute 'get_transcript'`
            # It's likely `get_transcript` is a static method but maybe I imported it wrong or version mismatch.
            # Correct usage is `YouTubeTranscriptApi.get_transcript(video_id)`.
            
            # Let's try fixing the youtube-transcript-api call first in a separate script file to debug.
            pass
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fetch_transcript(sys.argv[1])
