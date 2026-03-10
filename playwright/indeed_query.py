from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time

def search_job(name, location):

    with Stealth().use_sync(sync_playwright()) as p:
         # 2. Launch with headless=False
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        
        # 3. Use a standard, up-to-date User-Agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        page = context.new_page()

        try:
            page.goto("https://in.indeed.com/")
            
            # Wait a few seconds to allow the Cloudflare challenge to pass
            page.wait_for_timeout(3000) 
            
            print("Title:", page.title())
            page.get_by_placeholder('Job title, keywords, or company').fill(name)
            page.get_by_placeholder('City, state, zip code, or "remote"').fill(location)
            page.get_by_role('button', name='Find jobs').click()
            page.screenshot(path="indeed_homepage.png")


            
        except Exception as e:
            print(f"An error occurred: {e}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    search_job("python", "Chennai")