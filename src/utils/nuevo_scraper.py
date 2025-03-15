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
                break  

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

        return self.extract_news(soup, last_scraped_date)

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
                center_content = news_body.find_next(class_="center-content")
                title = center_content.find("h2").find("a").text.strip()
                source_link = center_content.find("h2").find("a")["href"]

                content_div = news_body.find("div", class_="news-content")
                content = content_div.text.strip() if content_div else ""

                news_submitted = center_content.find("div", class_="news-submitted")
                published_timestamp = int(news_submitted.find_all("span", attrs={"data-ts": True})[-1].get("data-ts"))
                published_date = datetime.fromtimestamp(published_timestamp).strftime("%Y-%m-%d %H:%M:%S")

                if last_scraped_date and published_date <= last_scraped_date:
                    print(f"Skipping already scraped news: {title} ({published_date})")
                    continue  

                user_link = news_submitted.find("a", href=re.compile("/user/.+/history"))
                user = user_link.text.strip() if user_link else "Desconocido"

                source_span = news_submitted.find("span", class_="showmytitle")
                source = source_span.text.strip() if source_span else "Desconocido"

                news_details = news_body.find_next(class_="news-details")

                comments = int(news_details.select_one("a.comments")["data-comments-number"]) if news_details.select_one("a.comments") else 0
                positive_votes = int(news_details.select_one("span.positive-vote-number").text) if news_details.select_one("span.positive-vote-number") else 0
                anonymous_votes = int(news_details.select_one("span.anonymous-vote-number").text) if news_details.select_one("span.anonymous-vote-number") else 0
                negative_votes = int(news_details.select_one("span.negative-vote-number").text) if news_details.select_one("span.negative-vote-number") else 0
                karma = int(news_details.select_one("span.karma-number").text) if news_details.select_one("span.karma-number") else 0
                category = news_details.select_one("a.subname").text.strip() if news_details.select_one("a.subname") else "Desconocido"

                clicks_span = news_body.find("span", id=f"clicks-number-{news_id}")
                clicks = int(clicks_span.text.strip()) if clicks_span else 0

                votes_a = news_body.find("a", id=f"a-votes-{news_id}")
                meneos = int(votes_a.text.strip()) if votes_a else 0

                story_link = news_summary.find("a", href=re.compile("^/story/"))
                full_story_link = f"{self.base_url}{story_link['href']}" if story_link else "Desconocido"

                scraped_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                new_entries.append({
                    "news_id": news_id, "title": title, "content": content, "full_story_link": full_story_link,
                    "meneos": meneos, "clicks": clicks, "karma": karma, "positive_votes": positive_votes,
                    "anonymous_votes": anonymous_votes, "negative_votes": negative_votes, "category": category,
                    "comments": comments, "published_date": published_date, "user": user, "source": source,
                    "source_link": source_link, "scraped_date": scraped_date
                })

            except Exception as e:
                print(f"Error procesando noticia: {e}")
                continue

        return new_entries

    def get_next_scraped_filename(self):
        existing_files = list(self.data_dir.glob("meneame_scraped_*.csv"))
        
        if not existing_files:
            return self.data_dir / "meneame_scraped_1.csv"

        numbers = [int(re.search(r"meneame_scraped_(\d+)\.csv", str(f)).group(1)) for f in existing_files if re.search(r"meneame_scraped_(\d+)\.csv", str(f))]

        next_number = max(numbers) + 1 if numbers else 1
        return self.data_dir / f"meneame_scraped_{next_number}.csv"

    def save_new_data(self, new_data):
        new_filename = self.get_next_scraped_filename()
        pd.DataFrame(new_data).to_csv(new_filename, index=False, encoding="utf-8")

    def get_latest_scraped_file(self):
        files = glob.glob(str(self.data_dir / "meneame_scraped_*.csv"))
        return max(files, key=os.path.getmtime) if files else None

    def get_last_scraped_date(self):
        latest_file = self.get_latest_scraped_file()
        return pd.read_csv(latest_file, usecols=["scraped_date"]).max()["scraped_date"] if latest_file else None
