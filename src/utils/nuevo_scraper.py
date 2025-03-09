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
    def __init__(self, max_pages=50, save_interval=50, data_dir="../00.data/scraped"):
        self.base_url = "https://meneame.net"
        self.max_pages = max_pages
        self.save_interval = save_interval
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def scrape(self):
        """Scrape new news from Meneame and save the data."""
        last_scraped_date = self.get_last_scraped_date()
        results = []

        for page in range(1, self.max_pages + 1):
            scraped_data = self.scrape_page(page, last_scraped_date)
            if scraped_data == "STOP":
                break
            results.extend(scraped_data)
            time.sleep(random.uniform(1, 2))  # Avoid detection

        if results:
            self.save_new_data(results)
            return f"✅ {len(results)} nuevas noticias guardadas."
        else:
            return "⚠️ No hay nuevas noticias."

    def scrape_page(self, page_number, last_scraped_date):
        """Scrape a single page from Meneame."""
        url = f"{self.base_url}/?page={page_number}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'es-ES,es;q=0.9'
        }

        print(f"🌐 [DEBUG] Scraping page {page_number} - URL: {url}")

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ [DEBUG] Error en {url}: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "lxml")

        extracted_news = self.extract_news(soup, last_scraped_date)
        print(f"📰 [DEBUG] Extracted {len(extracted_news)} news from page {page_number}")

        return extracted_news


    def extract_news(self, soup, last_scraped_date):
        """Extracts news from a soup object."""
        newswrap = soup.find(id="newswrap")
        if not newswrap:
            print("⚠️ [DEBUG] No news wrap found!")
            return []

        news_summaries = newswrap.find_all(class_="news-summary")
        print(f"🔍 [DEBUG] Found {len(news_summaries)} news summaries on this page.")

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

                print(f"🗞 [DEBUG] Checking: {title} ({published_date}) against last scraped {last_scraped_date}")

                # Stop if news is already scraped
                if last_scraped_date and published_date <= last_scraped_date:
                    print(f"🚨 [DEBUG] Skipping: {title} ({published_date}) - Already scraped!")
                    continue  # Instead of returning STOP, just continue

                new_entries.append({
                    "news_id": news_id, "title": title, "published_date": published_date
                })

            except Exception as e:
                print(f"⚠️ [DEBUG] Error processing news: {e}")
                continue

        return new_entries


    def save_new_data(self, new_data):
        """Save only new scraped data to a new file."""
        latest_file = self.get_latest_scraped_file()

        if latest_file and os.path.exists(latest_file):
            existing_df = pd.read_csv(latest_file, encoding="utf-8")
            new_df = pd.DataFrame(new_data)
            new_rows = new_df[~new_df.apply(tuple, 1).isin(existing_df.apply(tuple, 1))]

            if new_rows.empty:
                print("⚠️ No new rows to save.")
                return
        else:
            new_rows = pd.DataFrame(new_data)

        new_filename = self.get_next_scraped_filename()
        new_rows.to_csv(new_filename, index=False, encoding="utf-8")
        print(f"📁 {len(new_rows)} new rows saved in {new_filename}")

    def get_latest_scraped_file(self):
        """Get the most recent scraped file."""
        files = glob.glob(str(self.data_dir / "meneame_scraped_*.csv"))

        if not files:
            print("⚠️ [DEBUG] No scraped files found in:", self.data_dir)
            return None

        latest_file = max(files, key=os.path.getmtime)
        print(f"📂 [DEBUG] Latest scraped file: {latest_file}")
        
        return latest_file


    def get_last_scraped_date(self):
        """Get the last scraped date."""
        latest_file = self.get_latest_scraped_file()
        
        if not latest_file:
            print("⚠️ [DEBUG] No previous scraped file found.")
            return None  

        df = pd.read_csv(latest_file, usecols=["scraped_date"], encoding="utf-8")

        if df.empty:
            print("⚠️ [DEBUG] The scraped file is empty.")
            return None

        last_date = df["scraped_date"].max()
        print(f"📅 [DEBUG] Last scraped date in Streamlit: {last_date}")

        return last_date

