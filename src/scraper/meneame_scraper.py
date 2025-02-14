from dataclasses import dataclass, field, asdict
from datetime import datetime

import requests
import pandas as pd
import time
import random
from bs4 import BeautifulSoup

from src.model.meneame_entry import MeneameEntry


@dataclass
class MeneameScraper:
    base_url: str = "https://www.meneame.net"
    max_pages: int = 50
    save_interval: int = 5
    results: list[MeneameEntry]= field(default_factory=list)

    def scrape_page(self, page_number):
        """Scrapea una única página."""
        url = f"{self.base_url}/?page={page_number}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

        print(f"\n🟢 Scrapeando página {page_number}: {url}")

        response = requests.get(url, headers=headers)
        print(f"🔍 Status code: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Error en {url}: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "lxml")
        return self.extract_news(soup)

    def extract_news(self, soup) -> list[MeneameEntry]:
        tmp_results = []
        # Obtener el elemento con id newswrap
        newswrap = soup.find(id="newswrap")
        if not newswrap:
            raise ValueError("No se encontró el elemento 'newswrap'")

        # Obtener todos los elementos con la clase news-summary incluidos en newswrap
        news_summaries = newswrap.find_all(class_="news-summary")
        for news_summary in news_summaries:
            # Validar existencia de news-body
            news_body = news_summary.find(class_="news-body")

            # Extraer data-link-id
            news_id = int(news_body.get("data-link-id"))

            # Manejar posibles ausencias de news-shakeit
            news_shakeit = news_body.find_next(class_="news-shakeit")
            center_content = news_body.find_next(class_="center-content")
            title = center_content.find("h2").find("a").text.strip()
            news_submitted = center_content.find("div", class_="news-submitted")
            spans_with_data_ts= news_submitted.find_all("span", attrs={"data-ts": True})

            # Extraer fecha de publicacion en formato timestamp
            published_timestamp = int(spans_with_data_ts[-1].get("data-ts"))

            # Extraer comentarios
            news_details = news_body.find_next(class_="news-details")
            comments = int(news_details.select_one("a.comments").get("data-comments-number"))

            # Extraer votos positivos, anonimos y negativos
            positives_votes = int(news_details.select_one("span.positive-vote-number").text)
            anonymous_votes = int(news_details.select_one("span.anonymous-vote-number").text)
            negatives_votes = int(news_details.select_one("span.negative-vote-number").text)

            # Extraer karma
            karma_number = int(news_details.select_one("span.karma-number").text)

            # Extraer categoria
            category = news_details.select_one("a.subname").text

            # Extraer clics
            clics_span = news_shakeit.find("span", id=f"clicks-number-{news_id}")
            clicks_number = int(clics_span.text.strip()) if clics_span else 0

            # Extraer votos
            votes_a = news_shakeit.find("a", id=f"a-votes-{news_id} ga-event")
            meneos_number = int(votes_a.text.strip()) if votes_a else 0

            tmp_results.append(
                MeneameEntry(news_id,
                             title,
                             meneos_number,
                             clicks_number,
                             karma_number,
                             positives_votes,
                             anonymous_votes,
                             negatives_votes,
                             category,
                             comments,
                             published_timestamp,
                             int(datetime.now().timestamp())
                )
            )

        return tmp_results

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

                # Espera entre 4 y 10 segundos para evitar detección
                sleep_time = random.uniform(5, 10)
                print(f"⏳ Esperando {sleep_time:.2f} segundos antes de la siguiente página...")
                time.sleep(sleep_time)

            except Exception as e:
                print(f"⚠️ Error en la página {page}: {e}")
                continue

        # Guardar los datos finales
        self.save_final_data()

        # 🔴 Finalizar tiempo de ejecución
        end_time = time.time()
        elapsed_time = end_time - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        print(f"🏁 Scraping finalizado en {minutes}m {seconds}s.")

    def save_temp_data(self, page):
        """Guarda datos temporalmente cada X páginas."""
        df_temp = pd.DataFrame(self.results_as_dict_array)
        df_temp.to_csv(f"meneame_scraped_temp_{page}.csv", index=False, encoding="utf-8")
        print(f"📁 Datos guardados temporalmente en meneame_scraped_temp_{page}.csv")

    def save_final_data(self):
        """Guarda los datos finales en un CSV."""
        df = pd.DataFrame(self.results_as_dict_array)
        df.to_csv("meneame_scraped_final.csv", index=False, encoding="utf-8")
        print("✅ Scraping finalizado. Datos guardados en meneame_scraped_final.csv")

    @property
    def results_as_dict_array(self):
        return [asdict(x) for x in self.results]

# Ejemplo de prueba
my_scraper = MeneameScraper(max_pages=22, save_interval=5)
my_scraper.scrape_main_page()
