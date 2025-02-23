import time
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

#Importa la clase MeneameEntry para estructurar los datos de las noticias

from src.model.meneame_entry import MeneameEntry

class MeneameScraper:
    def __init__(self, max_pages=50, save_interval=5):
        self.base_url = "https://meneame.net"
        self.max_pages = max_pages
        self.save_interval = save_interval
        self.results = []
        self.failed_pages = []  # Lista para almacenar páginas con errores

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
        return self.extract_news(soup, page_number)

    def extract_news(self, soup, page_number):
        """Extrae información de las noticias de una página."""
        newswrap = soup.find(id="newswrap")
        if not newswrap:
            print(f"⚠️ No se encontró 'newswrap' en la página {page_number}. Guardando página para revisión.")
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
        
        #Buscar el cuerpo de la noticia dentro del resumen.
        
        news_body = news_summary.find(class_="news-body")
        
        #Si no se encuentra el cuerpo, continuar con la siguiente noticia.
        if not news_body:
            continue
        
        #Extraer el ID de la noticia.
        
        news_id = int(news_body.get("data-link-id"))
        
        #Buscar el contenido central de la noticia (título, enlace, etc.).
        
        center_content = news_body.find_next(class_="center-content")
        
        #Extraer el título de la noticia.
        
        title = center_content.find("h2").find("a").text.strip()
        
        #Extraer el enlace fuente de la noticia.
        
        source_link = center_content.find("h2").find("a")["href"]
        
        #Extraer el contenido de la noticia, si está disponible.
        
        content_div = news_body.find("div", class_="news-content")
        content = content_div.text.strip() if content_div else ""
        
        #Buscar la fecha de publicación de la noticia.
        
        news_submitted = center_content.find("div", class_="news-submitted")
        published_timestamp = int(news_submitted.find_all("span", attrs={"data-ts": True})[-1].get("data-ts"))
        published_date = datetime.fromtimestamp(published_timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        #Extraer el nombre del usuario que publicó la noticia.
        
        user_link = news_submitted.find("a", href=re.compile("/user/.+/history"))
        user = user_link.text.strip() if user_link else "Desconocido"
        
        #Extraer la fuente de la noticia, si está disponible.
        
        source_span = news_submitted.find("span", class_="showmytitle")
        source = source_span.text.strip() if source_span else "Desconocido"
        
        #Buscar detalles adicionales como votos y comentarios.
        
        news_details = news_body.find_next(class_="news-details")
        comments = int(news_details.select_one("a.comments").get("data-comments-number"))
        positive_votes = int(news_details.select_one("span.positive-vote-number").text)
        anonymous_votes = int(news_details.select_one("span.anonymous-vote-number").text)
        negative_votes = int(news_details.select_one("span.negative-vote-number").text)
        karma = int(news_details.select_one("span.karma-number").text)
        category = news_details.select_one("a.subname").text.strip()
        
        #Extraer información de clicks y meneos
        
        clicks_span = news_body.find("span", id=f"clicks-number-{news_id}")
        clicks = int(clicks_span.text.strip()) if clicks_span else 0
        votes_a = news_body.find("a", id=f"a-votes-{news_id} ga-event")
        meneos = int(votes_a.text.strip()) if votes_a else 0
        
        #Obtener el enlace completo de la historia
        
        story_link = news_summary.find("a", href=re.compile("^/story/"))
        full_story_link = f"{self.base_url}{story_link['href']}" if story_link else "Desconocido"
        
        #Registrar la fecha en la que se está realizando el scraping
        
        scraped_date = datetime.now().strftime("%Y-%m-%d")
        
        #Crear un objeto MeneameEntry con toda la información de la noticia
        
        results.append(MeneameEntry(
            news_id, title, content, full_story_link, meneos, clicks, karma, positive_votes, anonymous_votes, negative_votes,
            category, comments, published_date, user, source, source_link, scraped_date
        ))
    
    except Exception as e:
        # Si ocurre un error, imprimir el error y agregar la página a la lista de fallidas
        print(f"⚠️ Error procesando noticia en página {page_number}: {e}. Continuando con la siguiente noticia.")
        self.failed_pages.append(page_number)
        continue

# Devolver todos los resultados procesados
return results

   def scrape_main_page(self, start_page=1):
        """Itera por las páginas manualmente usando ?page=X."""
        start_time = time.time()

        for page in range(start_page, self.max_pages + 1):
            try:
                new_data = self.scrape_page(page)
                self.results.extend(new_data)

                if page % self.save_interval == 0:
                    self.save_temp_data(page)

                # Espera entre 1 y 2 segundos para evitar detección
                sleep_time = random.uniform(1, 2)
                print(f"⏳ Esperando {sleep_time:.2f} segundos antes de la siguiente página...")
                time.sleep(sleep_time)

            except Exception as e:
                print(f"⚠️ Error en la página {page}: {e}")
                break

        self.save_final_data()
        self.save_failed_pages()  # Guardamos páginas con errores
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

    #Función que guarda las páginas que fallaron en un archivo csv, e imprimelas.

    def save_failed_pages(self):
        """Guarda en un archivo CSV las páginas que tuvieron menos de 25 noticias o errores."""
        if self.failed_pages:
            df_failed = pd.DataFrame({"failed_pages": self.failed_pages})
            df_failed.to_csv("meneame_failed_pages.csv", index=False, encoding="utf-8")
            print(f"⚠️ Páginas problemáticas guardadas en meneame_failed_pages.csv")
        else:
            print("✅ No se detectaron páginas problemáticas.")


# Ejemplo para ejecutar el scraper
# scraper = MeneameScraper(max_pages=12000, save_interval=100)
# scraper.scrape_main_page(start_page=6194)
