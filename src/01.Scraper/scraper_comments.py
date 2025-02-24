import requests
import pandas as pd
import json
import time
from multiprocessing import Pool


df = pd.read_csv("/Users/iclon/Downloads/meneame_scraped_final_3 (1).csv")
news_ids = df["news_id"].astype(str).tolist()  # Convertir a string por si acaso


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
}


def get_comments(news_id):
    url = f"https://www.meneame.net/api/list.php?id={news_id}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            comments_list = data.get("objects", [])
            
     
            comments = [comment["content"].strip() for comment in comments_list[:10] if "content" in comment]
            
            return {"news_id": news_id, "top_10_comments": json.dumps(comments, ensure_ascii=False)}
        else:
            return {"news_id": news_id, "top_10_comments": "[]"}
    except Exception as e:
        return {"news_id": news_id, "top_10_comments": "[]"}

#multiprocessing
if __name__ == "__main__":
    with Pool(10) as p:
        results = []
        for i, result in enumerate(p.imap(get_comments, news_ids), 1):  # Procesa en paralelo
            results.append(result)

  
            if i % 1000 == 0:
                print(f"{i} noticias procesadas...")


            if i % 5000 == 0:
                pd.DataFrame(results).to_csv("meneame_comments_data.csv", index=False)


    comments_df = pd.DataFrame(results)
    comments_df.to_csv("meneame_comments_data.csv", index=False)

    print("Nuevo CSV creado con éxito: 'meneame_comments_data.csv'.")