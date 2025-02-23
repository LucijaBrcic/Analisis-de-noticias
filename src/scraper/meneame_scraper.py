import time
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# Importa la clase MeneameEntry para estructurar los datos de las noticias
from src.model.meneame_entry import MeneameEntry

class MeneameScraper:
    def __init__(self, max_pages=50, save_interval=5):
        """
        Inicializa el scraper con los parámetros dados.
        :param max_pages: Número máximo de páginas a scrapear.
        :param save_interval: Cada cuántas páginas se guardan los datos temporalmente.
        """
        self.base_url = "https://meneame.net"
        self.max_pages = max_pages
        self.save_interval = save_interval
        self.results = []  # Lista para almacenar noticias extraídas
        self.failed_pages = []  # Lista para registrar páginas con errores

    def scrape_page(self, page_number):
        """
        Realiza una solicitud HTTP a una página de Menéame y extrae noticias.
        :param page_number: Número de página a scrapear.
        :return: Lista de objetos MeneameEntry extraídos.
        """
        url = f"{self.base_url}/?page={page_number}"
        headers = {'User-Agent': 'Mozilla/5.0'}

        print(f"\n🟢 Scrapeando página {page_number}: {url}")
        try:
            response = requests.get(url, headers=headers)
            print(f"🔍 Status code: {response.status_code}")

            if response.status_code != 200:
                print(f"❌ Error al acceder a {url}")
                self.failed_pages.append(page_number)
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            return self.extract_news(soup, page_number)
        except requests.RequestException as e:
            print(f"⚠️ Error en la solicitud HTTP para página {page_number}: {e}")
            self.failed_pages.append(page_number)
            return []

    def extract_news(self, soup, page_number):
        """
        Extrae información de las noticias de una página web parseada con BeautifulSoup.
        :param soup: Objeto BeautifulSoup de la página.
        :param page_number: Número de página actual.
        :return: Lista de objetos MeneameEntry.
        """
        newswrap = soup.find(id="newswrap")
        if not newswrap:
            print(f"⚠️ No se encontró 'newswrap' en la página {page_number}.")
            self.failed_pages.append(page_number)
            return []

        news_summaries = newswrap.find_all(class_="news-summary")
        print(f"✅ Noticias encontradas en página {page_number}: {len(news_summaries)}")

        if len(news_summaries) < 25:
            print(f"⚠️ Página {page_number} tiene menos de 25 noticias. Posible problema.")
            self.failed_pages.append(page_number)

        results = []
        for news_summary in news_summaries:
            try:
                news_body = news_summary.find(class_="news-body")
                if not news_body:
                    continue
                
                news_id = int(news_body.get("data-link-id", 0))
                title_tag = news_body.find("h2").find("a")
                title = title_tag.text.strip() if title_tag else "Sin título"
                source_link = title_tag["href"] if title_tag else ""
                
                content_div = news_body.find("div", class_="news-content")
                content = content_div.text.strip() if content_div else ""

                # Fecha de publicación
                news_submitted = news_body.find("div", class_="news-submitted")
                published_span = news_submitted.find("span", attrs={"data-ts": True})
                published_timestamp = int(published_span["data-ts"]) if published_span else 0
                published_date = datetime.fromtimestamp(published_timestamp).strftime("%Y-%m-%d %H:%M:%S")

                # Usuario y fuente
                user_tag = news_submitted.find("a", href=re.compile("/user/.+/history"))
                user = user_tag.text.strip() if user_tag else "Desconocido"
                
                source_span = news_submitted.find("span", class_="showmytitle")
                source = source_span.text.strip() if source_span else "Desconocido"

                # Comentarios y votos
                news_details = news_body.find_next(class_="news-details")
                comments = int(news_details.select_one("a.comments").get("data-comments-number", 0))
                positive_votes = int(news_details.select_one("span.positive-vote-number").text)
                karma = int(news_details.select_one("span.karma-number").text)
                
                story_link = news_summary.find("a", href=re.compile("^/story/"))
                full_story_link = f"{self.base_url}{story_link['href']}" if story_link else "Desconocido"
                
                scraped_date = datetime.now().strftime("%Y-%m-%d")
                
                results.append(MeneameEntry(
                    news_id, title, content, full_story_link, positive_votes, karma, comments, 
                    published_date, user, source, source_link, scraped_date
                ))
            except Exception as e:
                print(f"⚠️ Error procesando noticia en página {page_number}: {e}")
                self.failed_pages.append(page_number)
                continue
        
        return results

    def scrape_main_page(self, start_page=1):
        """
        Itera por las páginas desde start_page hasta max_pages y extrae noticias.
        """
        start_time = time.time()
        for page in range(start_page, self.max_pages + 1):
            try:
                new_data = self.scrape_page(page)
                self.results.extend(new_data)
                if page % self.save_interval == 0:
                    self.save_temp_data(page)
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"⚠️ Error en la página {page}: {e}")
                break
        self.save_final_data()
        self.save_failed_pages()
        print(f"🏁 Scraping finalizado en {time.time() - start_time:.2f} segundos.")

    def save_temp_data(self, page):
        """Guarda datos temporalmente cada cierto número de páginas."""
        df_temp = pd.DataFrame([entry.to_dict() for entry in self.results])
        df_temp.to_csv(f"meneame_scraped_temp_{page}.csv", index=False, encoding="utf-8")
        print(f"📁 Datos guardados temporalmente en meneame_scraped_temp_{page}.csv")

    def save_final_data(self):
        """Guarda los datos finales en un CSV."""
        df = pd.DataFrame([entry.to_dict() for entry in self.results])
        df.to_csv("meneame_scraped_final.csv", index=False, encoding="utf-8")
        print("✅ Datos guardados en meneame_scraped_final.csv")
