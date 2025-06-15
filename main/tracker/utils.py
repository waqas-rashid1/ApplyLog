# utils.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def detect_job_source(url):
    domain = urlparse(url).netloc
    clean_source = domain.replace('www.', '').split('.')[0]
    return clean_source.capitalize()

def fetch_job_details(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        title = (
            soup.find("h1") or
            soup.find("meta", property="og:title") or
            soup.title
        )

        company = soup.find(string=lambda t: "Company" in t or "About" in t)
        deadline = soup.find(string=lambda t: "Deadline" in t or "Apply before" in t)

        return {
            "job_title": title.get_text(strip=True) if hasattr(title, 'get_text') else title,
            "company": company.strip() if company else None,
            "deadline": deadline.strip() if deadline else None
        }

    except Exception as e:
        print("Scraping error:", e)
        return {}
