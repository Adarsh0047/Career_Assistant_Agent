from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time
import json

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
            # Locate all job cards on the page
            page.locator('.cardOutline').first.wait_for()
            job_cards = page.locator('.cardOutline').all()
            # print(job_cards)

            url_dict = {}
            # scraped_jobs = []
            for job in job_cards:

                # If the job is not visible, then skip
                if not job.is_visible():
                    continue
                # Extract Title, Company, and Location
                title = job.locator('.jobTitle').inner_text().strip()
                company = job.locator('[data-testid="company-name"]').inner_text().strip()
                job_location = job.locator('[data-testid="text-location"]').inner_text().strip()

                # Locate the clickable title element
                title_element = job.locator('.jcs-JobTitle')
                
                # Extract the relative URL from the href attribute
                relative_url = title_element.get_attribute('href')
                
                # Construct the full absolute URL
                full_url = f"https://in.indeed.com{relative_url}" if relative_url else "No URL found"
                
                url_dict[full_url] = {
                    "title": title,
                    "company": company,
                    "job_location": job_location
                }
                # Print the extracted details
                print(f"Title: {title}")
                print(f"Company: {company}")
                print(f"Location: {job_location}")
                print(f"URL: {full_url}")
                

                title_element.scroll_into_view_if_needed(timeout=3000)
                try:
                    title_element.click(timeout=3000)
                except:
                    print("Click blocked! Attempting to close popup...")
                    # Try hitting escape to close standard modals
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(1000)
                
                page.wait_for_timeout(2000)
                print("-" * 60)

                 # 3. Wait for the right pane's description to load
                # This ensures the new job has fully populated in the right panel
                page.locator('#jobDescriptionText').wait_for(state="visible", timeout=5000)
                
                # --- EXTRACTION FROM RIGHT PANE ---
                
                # Extract Job Name (often contains "- job post" which we can strip)
                pane_job_name = page.locator('h2[data-testid="jobsearch-JobInfoHeader-title"]').inner_text()
                pane_job_name = pane_job_name.replace("- job post", "").strip()

                # Extract Job Details (e.g., Job type, Shift, etc.)
                job_details_text = "N/A"
                if page.locator('#jobDetailsSection').count() > 0:
                    job_details_text = page.locator('#jobDetailsSection').inner_text().strip()

                # Extract Full Description
                full_description = page.locator('#jobDescriptionText').inner_text().strip()

                # Extract Skills (Parsing the description text to find lines mentioning "skills")
                skills_text =[]
                for line in full_description.split('\n'):
                    if "skills" in line.lower():
                        skills_text.append(line.strip())
                skills_joined = " | ".join(skills_text) if skills_text else "Not explicitly listed"

                # Save to dictionary
                job_data = {
                    "Job Name": pane_job_name,
                    "Company": company,
                    "Job Details": job_details_text,
                    "Skills": skills_joined,
                    "Full Description": full_description
                }
                url_dict[full_url]["job_data"] = job_data
                # scraped_jobs.append(job_data)

                # Print out the extracted right-pane data
                print(f"Right Pane Title : {job_data['Job Name']}")
                print(f"Right Pane Details:\n{job_data['Job Details']}")
                print(f"Parsed Skills    : {job_data['Skills']}")
                print(f"Description Len  : {len(job_data['Full Description'])} characters")
                print("-" * 60)
            
            # print(f"Successfully scraped {len(scraped_jobs)} jobs.")

            page.screenshot(path="indeed_homepage.png")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        finally:
            browser.close()
    with open("urls.json", "w") as f:
        json.dump(url_dict, f)

if __name__ == "__main__":
    search_job("python", "Chennai")