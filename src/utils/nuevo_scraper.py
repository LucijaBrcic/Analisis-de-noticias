import os
import re
import time
import random
import glob
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

class MeneameScraper:
    def __init__(self, save_interval=50, data_dir="../00.data/scraped"):
        self.base_url = "https://meneame.net"
        self.save_interval = save_interval
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def scrape(self):
        last_scraped_date = self.get_last_scraped_date()
        results = []
        page = 1  

        while True:
            scraped_data = self.scrape_page(page, last_scraped_date)
            if not scraped_data:  
                break  # Stop when there are no new articles

            results.extend(scraped_data)
            page += 1  
            time.sleep(random.uniform(1, 2))

        if results:
            self.save_new_data(results)
            return f"{len(results)} nuevas noticias guardadas."
        else:
            return "No hay nuevas noticias."

    def scrape_page(self, page_number, last_scraped_date):
        url = f"{self.base_url}/?page={page_number}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'es-ES,es;q=0.9'
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "lxml")

        extracted_news = self.extract_news(soup, last_scraped_date)

        return extracted_news

    def extract_news(self, soup, last_scraped_date):
        newswrap = soup.find(id="newswrap")
        if not newswrap:
            return []

        news_summaries = newswrap.find_all(class_="news-summary")

        new_entries = []

        for news_summary in news_summaries:
            try:
                news_body = news_summary.find(class_="news-body")
                if not news_body:
                    continue

                news_id = int(news_body.get("data-link-id"))
                title = news_body.find("h2").find("a").text.strip()

                published_timestamp = int(news_body.find("span", attrs={"data-ts": True})["data-ts"])
                published_date = datetime.fromtimestamp(published_timestamp).strftime("%Y-%m-%d %H:%M:%S")

                if last_scraped_date and published_date <= last_scraped_date:
                    return []  # Stop when reaching an already scraped news

                new_entries.append({
                    "news_id": news_id,
                    "title": title,
                    "published_date": published_date,
                    "scraped_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            except Exception as e:
                continue

        return new_entries
    
    def get_next_scraped_filename(self):
        """Generate the next filename for saving scraped data."""
        existing_files = list(self.data_dir.glob("meneame_scraped_*.csv"))
        
        if not existing_files:
            return self.data_dir / "meneame_scraped_1.csv"

        # Extract numbers from existing files
        numbers = []
        for file in existing_files:
            match = re.search(r"meneame_scraped_(\d+)\.csv", str(file))
            if match:
                numbers.append(int(match.group(1)))

        next_number = max(numbers) + 1 if numbers else 1
        return self.data_dir / f"meneame_scraped_{next_number}.csv"


    def save_new_data(self, new_data):
        latest_file = self.get_latest_scraped_file()

        if latest_file and os.path.exists(latest_file):
            existing_df = pd.read_csv(latest_file, encoding="utf-8")
            new_df = pd.DataFrame(new_data)
            new_rows = new_df[~new_df.apply(tuple, 1).isin(existing_df.apply(tuple, 1))]

            if new_rows.empty:
                return
        else:
            new_rows = pd.DataFrame(new_data)

        new_filename = self.get_next_scraped_filename()
        new_rows.to_csv(new_filename, index=False, encoding="utf-8")

    def get_latest_scraped_file(self):
        files = glob.glob(str(self.data_dir / "meneame_scraped_*.csv"))

        if not files:
            return None

        latest_file = max(files, key=os.path.getmtime)
        
        return latest_file

    def get_last_scraped_date(self):
        latest_file = self.get_latest_scraped_file()
        
        if not latest_file:
            return None  

        df = pd.read_csv(latest_file, usecols=["scraped_date"], encoding="utf-8")

        if df.empty:
            return None

        last_date = df["scraped_date"].max()

        return last_date
