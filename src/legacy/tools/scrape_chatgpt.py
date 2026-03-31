import asyncio
import os
import sys
from pathlib import Path

# Try importing playwright, if not present, instruct user
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright is not installed. Please run:")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)

TARGET_URL = "https://chatgpt.com/share/69738a16-95f4-8010-90a1-3c5444b4ab03"
OUTPUT_FILE = "data/inputs/chatgpt_context.txt"

async def scrape_chatgpt():
    print(f"[INFO] Launching browser to fetch: {TARGET_URL}")
    print("[INFO] Note: Browser will open. Please solve any CAPTCHAs or login if requested.")
    
    async with async_playwright() as p:
        # Launch non-headless so user can interact/solve Cloudflare
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            await page.goto(TARGET_URL)
            
            # Wait for content to load
            print("[INFO] Waiting for conversation to load...")
            # We wait for a typical element in shared links
            try:
                # Wait up to 60 seconds (or more if user needs to solve captcha)
                # We'll wait for the main conversation container
                await page.wait_for_selector("div.markdown", timeout=60000) 
            except Exception:
                print("[WARN] Timeout waiting for automatic detection. Please ensure the page is loaded.")
                input("Press Enter here when the page is fully loaded to continue scraping...")

            # Extract text
            content = await page.evaluate("""() => {
                return document.body.innerText;
            }""")
            
            # Save to file
            out_path = Path(OUTPUT_FILE)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
            
            print(f"[SUCCESS] Content saved to: {out_path.absolute()}")
            print("[INFO] You can close the browser now.")
            
        except Exception as e:
            print(f"[ERROR] Failed to scrape: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_chatgpt())
