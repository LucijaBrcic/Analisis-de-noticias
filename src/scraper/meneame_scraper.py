import time
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

from src.model.meneame_entry import MeneameEntry

# Diccionario de provincias y comunidades autónomas de España
PROVINCIAS_COMUNIDADES = {
    "Madrid": "Comunidad de Madrid", "Barcelona": "Cataluña", "Valencia": "Comunidad Valenciana", "Sevilla": "Andalucía",
    "Zaragoza": "Aragón", "Málaga": "Andalucía", "Murcia": "Región de Murcia", "Palma": "Islas Baleares",
    "Las Palmas": "Canarias", "Bilbao": "País Vasco", "Alicante": "Comunidad Valenciana", "Córdoba": "Andalucía",
    "Valladolid": "Castilla y León", "Vigo": "Galicia", "Gijón": "Asturias", "Hospitalet": "Cataluña",
    "La Coruña": "Galicia", "Granada": "Andalucía", "Vitoria": "País Vasco", "Elche": "Comunidad Valenciana",
    "Oviedo": "Asturias", "Santa Cruz de Tenerife": "Canarias", "Badalona": "Cataluña", "Cartagena": "Murcia"
}


class MeneameScraper:
    def __init__(self, max_pages=50, save_interval=5):
        self.base_url = "https://meneame.net"
        self.max_pages = max_pages
        self.save_interval = save_interval
        self.results = []

    def scrape_page(self, page_number):
        """Scrapea una única página."""
        url = f"{self.base_url}/?page={page_number}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        
        print(f"\n🟢 Scrapeando página {page_number}: {url}")

        response = requests.get(url, headers=headers)
        print(f"🔍 Status code: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Error en {url}: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "lxml")
        return self.extract_news(soup)

    def extract_news(self, soup):
        """Extrae información de las noticias de una página."""
        newswrap = soup.find(id="newswrap")
        if not newswrap:
            print("⚠️ No se encontró 'newswrap'. Saltando página.")
            return []

        results = []
        news_summaries = newswrap.find_all(class_="news-summary")
        print(f"✅ Noticias encontradas: {len(news_summaries)}")

        for news_summary in newswrap.find_all(class_="news-summary"):
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

            author_link = news_submitted.find("a", href=re.compile("/user/.+/history"))
            author = author_link.text.strip() if author_link else "Desconocido"

            source_span = news_submitted.find("span", class_="showmytitle")
            source = source_span.text.strip() if source_span else "Desconocido"

            news_details = news_body.find_next(class_="news-details")
            comments = int(news_details.select_one("a.comments").get("data-comments-number"))
            positive_votes = int(news_details.select_one("span.positive-vote-number").text)
            anonymous_votes = int(news_details.select_one("span.anonymous-vote-number").text)
            negative_votes = int(news_details.select_one("span.negative-vote-number").text)
            karma = int(news_details.select_one("span.karma-number").text)
            category = news_details.select_one("a.subname").text.strip()

            clicks_span = news_body.find("span", id=f"clicks-number-{news_id}")
            clicks = int(clicks_span.text.strip()) if clicks_span else 0
            votes_a = news_body.find("a", id=f"a-votes-{news_id} ga-event")
            meneos = int(votes_a.text.strip()) if votes_a else 0

            scraped_date = datetime.now().strftime("%Y-%m-%d")
            provincia, comunidad = self.detect_province_region(title)

            results.append(MeneameEntry(
                news_id, title, content, meneos, clicks, karma, positive_votes, anonymous_votes, negative_votes, category,
                comments, published_date, author, source, source_link, provincia, comunidad, scraped_date
            ))
        return results

    def detect_province_region(self, title):
        for provincia, comunidad in PROVINCIAS_COMUNIDADES.items():
            if provincia.lower() in title.lower():
                return provincia, comunidad
        return "Desconocido", "Desconocido"

    def scrape_main_page(self):
        """Itera por las páginas manualmente usando ?page=X."""
        start_time = time.time()  # 🔴 Iniciar tiempo de ejecución

        for page in range(1, self.max_pages + 1):
            try:
                new_data = self.scrape_page(page)
                self.results.extend(new_data)

                # Guardar cada X páginas
                if page % self.save_interval == 0:
                    self.save_temp_data(page)

                # Espera entre 5 y 10 segundos para evitar detección
                sleep_time = random.uniform(4, 6)
                print(f"⏳ Esperando {sleep_time:.2f} segundos antes de la siguiente página...")
                time.sleep(sleep_time)

            except Exception as e:
                print(f"⚠️ Error en la página {page}: {e}")
                break

        self.save_final_data()
        elapsed_time = time.time() - start_time
        print(f"🏁 Scraping finalizado en {elapsed_time:.2f} segundos.")
        
    def save_temp_data(self, page):
        """Guarda datos temporalmente cada X páginas."""
        df_temp = pd.DataFrame([entry.to_dict() for entry in self.results])
        df_temp.to_csv(f"meneame_scraped_temp_{page}.csv", index=False, encoding="utf-8")
        print(f"📁 Datos guardados temporalmente en meneame_scraped_temp_{page}.csv")
       
    def save_final_data(self):
        """Guarda los datos finales en un CSV."""
        df = pd.DataFrame([entry.to_dict() for entry in self.results])
        df.to_csv("meneame_scraped_final.csv", index=False, encoding="utf-8")
        print("✅ Datos guardados en meneame_scraped_final.csv")