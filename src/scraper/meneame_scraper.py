import requests
from bs4 import BeautifulSoup


class MeneameScraper:
    def __init__(self):
        self.base_url = "https://www.meneame.net"

    def valid_suburls(self):
        return ["/", "/queue", "/articles", "/popular", "/top_visited"]

    def scrape(self, suburl_to_scrape):
        if suburl_to_scrape not in self.valid_suburls():
            raise ValueError("Invalid URL")

        # Include headers to avoid 403 error
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        resp = requests.get(f"{self.base_url}{suburl_to_scrape}", headers=headers)
        if resp.status_code != 200:
            raise ValueError(f"Error scraping the page, status code: {resp.status_code}")

        soup = BeautifulSoup(resp.text, "lxml")

        results = []

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
            news_id = news_body.get("data-link-id")

            # Manejar posibles ausencias de news-shakeit
            news_shakeit = news_body.find_next(class_="news-shakeit")
            center_content = news_body.find_next(class_="center-content")
            title = center_content.find("h2").find("a").text.strip()

            # Extraer clics
            clics_span = news_shakeit.find("span", id=f"clicks-number-{news_id}")
            clicks_number = int(clics_span.text.strip()) if clics_span else 0

            # Extraer votos
            votes_a = news_shakeit.find("a", id=f"a-votes-{news_id} ga-event")
            votes_number = int(votes_a.text.strip()) if votes_a else 0

            results.append({
                "title": title,
                "id": news_id,
                "clicks": clicks_number,
                "votes": votes_number
            })

        return results


# Ejemplo de prueba
my_scraper = MeneameScraper()
my_results = my_scraper.scrape("/top_visited")
print(my_results)