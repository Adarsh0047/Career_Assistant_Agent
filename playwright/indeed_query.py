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
            # Locate all job cards on the page
            page.locator('.cardOutline').first.wait_for()
            job_cards = page.locator('.cardOutline').all()
            print(job_cards)

            url_dict = {}
            for job in job_cards:
                # Extract Title, Company, and Location
                title = job.locator('.jobTitle').inner_text().strip()
                company = job.locator('[data-testid="company-name"]').inner_text().strip()
                job_location = job.locator('[data-testid="text-location"]').inner_text().strip()
                
                # Extract the relative URL from the href attribute
                relative_url = job.locator('.jcs-JobTitle').get_attribute('href')
                
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
                print("-" * 60)
            page.screenshot(path="indeed_homepage.png")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        try:
            for url, meta in url_dict.items():
                # print(url)
                try:
                    page.goto(url)
                    page.wait_for_timeout(3000)
                    # 1. Get Job Name (Title)
                    job_name = page.locator('h1[data-testid="jobsearch-JobInfoHeader-title"]').inner_text()
                    job_name.wait_for(timeout=5000) 
                    # 2. Get Job Details (Company, Location, Job Type)
                    company = page.locator('[data-testid="inlineHeader-companyName"]').inner_text()
                    location = page.locator('#jobLocationText').inner_text()
                    
                    # The Job Type (e.g., "Internship") is inside the job details section list items
                    job_type_elements = page.get_by_role("group", name="Job type").get_by_test_id("list-item").all_inner_texts()
                    job_type = ", ".join(job_type_elements) if job_type_elements else "Not specified"

                    pay_elements = page.get_by_role("group", name="Pay").get_by_test_id("list-item").all_inner_texts()
                    pay = ", ".join(pay_elements) if pay_elements else "Not specified"

                    # 4. Get Full Job Description
                    job_description = page.locator('#jobDescriptionText').inner_text()

                    # 5. Get Skills (Checking if the text exists first to prevent errors on pages without it)
                    skills_locator = page.locator('p', has_text="Required Skills:")
                    if skills_locator.count() > 0:
                        required_skills = skills_locator.first.inner_text().replace("Required Skills:", "").strip()
                    else:
                        required_skills = "Not explicitly listed"

                    # --- PRINT RESULTS ---
                    print(f"--- JOB NAME ---\n{job_name}\n")
                    print(f"--- JOB DETAILS ---\nCompany: {company}\nLocation: {location}\nType: {job_type}\nPay: {pay}\n")
                    print(f"--- SKILLS ---\n{required_skills}\n")
                    print(f"--- FULL DESCRIPTION ---\n{job_description}")
                except TimeoutError:
                    print(f"Cannot find the locator in the url: {url}")
                    continue
            
        finally:
            browser.close()

if __name__ == "__main__":
    search_job("python", "Chennai")