print("🔥 Test file is running...")

from scraper.job_scraper import scrape_indeed

role = "Software Engineer Intern"
location = "Remote"

print("🔍 Scraping jobs for:", role, "in", location)

jobs = scrape_indeed(role, location)

if not jobs:
    print("❌ No jobs found.")
else:
    for job in jobs:
        print(f"{job['title']} at {job['company']}")
        print(f"Link: {job['link']}")
        print("-" * 40)
