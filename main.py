import json, config

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from playwright.sync_api import Page

from data_base.jobs import clear_jobs, get_jobs, insert_jobs
from data_visualizer import JobDataVisualizer
from models import JobDescription
from parser.main_parser import *
from ai.job_info_extractor import *


load_dotenv()

email = config.email
email_pwd = config.email_pwd

def parse_data_from_linkedin():
    page_count_to_scrape = int(input("Enter the number of pages to scrape  📄 : "))
    if page_count_to_scrape <= 0:
        return print("❌ Invalid page count. Please enter a positive integer.")
    browser = sync_playwright().start().chromium.launch(headless=True)
    with browser:
        page = browser.new_page()
        parser = JobParser(page, email, email_pwd, "python developer", "USA", page_count_to_scrape)
        parser.login()
        print("[SCRAPING DATA ETAP 1️⃣  ] Logged in successfully.")
        parser.open_job_search()
        print("[SCRAPING DATA ETAP 2️⃣  ] Opened job search page.")
        job_data = parser.extract_job_data()
        print("[SCRAPING DATA ETAP 3️⃣  ] Extracted job data.")
        browser.close()
        if not job_data:
            raise ValueError("No job data found.")

        print("[SCRAPING DATA LOG] Total jobs extracted:", len(job_data))

    return job_data

def extract_with_ai(job_data):
    job_info_extractor = JobInfoExtractor()
    job_CVs = []
    for job in job_data:
        job_description = (job)
        response_from_ai = job_info_extractor.extract(job_description)
            
        try:
            print(f"🤖 AI Response:[{response_from_ai}]", "\n\n")
            job_info = json.loads(response_from_ai)
            cv = JobDescription(
                    job_title=str(job_info.get("job_title")),
                    company_name=str(job_info.get("company_name")),
                    location=str(job_info.get("location")),
                    salary=str(job_info.get("salary")),
                    job_type=str(job_info.get("job_type")),
                    hard_skills=str(job_info.get("hard_skills")),
                    soft_skills=str(job_info.get("soft_skills")),
                    work_mode=str(job_info.get("work_mode"))
            )
            job_CVs.append(cv)
        except json.JSONDecodeError as e:
            print(f"❌ Error decoding JSON: {e}")
    return job_CVs

def visualize_data():
    data_count_to_visualize = int(input("Enter the number of jobs to visualize 📊 : "))
    if data_count_to_visualize <= 0:
        return print("❌ Invalid count. Please enter a positive integer.")
    job_CVs = get_jobs(data_count_to_visualize)
    visualizer = JobDataVisualizer(job_CVs)   
    visualizer.plot_skills_bar("hard_skills")
    visualizer.plot_skills_bar("soft_skills")
    visualizer.plot_work_mode_pie()

def main():
    
    job_data = parse_data_from_linkedin()
    job_CVs = extract_with_ai(job_data)
    if not job_CVs:
        return
    # clear_jobs() # if you want to clear existing jobs before inserting new ones
    insert_jobs(job_CVs)
    visualize_data()


if __name__ == "__main__":
    main()
