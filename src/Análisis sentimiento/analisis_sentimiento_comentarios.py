import ast
import pandas as pd
from tqdm import tqdm
from transformers import pipeline
from concurrent.futures import ThreadPoolExecutor

#Inicializa la barra de prgreso de pandas

tqdm.pandas()

#modelo preentrenado de análisis de sentimiento

sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

#Función para convertir el string de comentarios a una lista (si es que está en formato string de lista)

def parse_comments(comment_str):
    try:
        return ast.literal_eval(comment_str)
    except (ValueError, SyntaxError):
        return []

#Función para analizar el sentimiento de un comentario

def analyze_sentiment_bert(comment):
    if not comment.strip():
        return 0

# Truncamos a 500 caracteres porque el modelo da problemas con más

 truncated_comment = comment[:500]  
  result = sentiment_pipeline(truncated_comment)[0]
  score = result["label"]  
    return int(score[0]) - 3
#Esta función toma un comentario de texto como entrada y devuelve un valor numérico que representa su sentimiento:
#Negativo → valores entre -2 y -1
#Neutro → 0
#Positivo → valores entre 1 y 2


file_path = "/Users/iclon/Desktop/meneame_comments_3.csv"
df = pd.read_csv(file_path)

#Convertir la columna de comentarios a listas reales.

df["parsed_comments"] = df["top_10_comments"].apply(parse_comments)

#Función para procesar una noticia (paralelizable).

def process_news(comments):
    return sum(analyze_sentiment_bert(c) for c in comments) / len(comments) if comments else 0

#Procesar en paralelo usando ThreadPoolExecutor para tardar menos.

with ThreadPoolExecutor() as executor:
    df["sentiment_score"] = list(tqdm(executor.map(process_news, df["parsed_comments"]), total=len(df)))
    
#Guardamos en DataFrame el análisis de sentimientos en un archivo csv.

df[["news_id", "sentiment_score"]].to_csv("sentiment_analysis_results.csv", index=False)

print("Análisis de sentimiento completado. Resultados guardados en 'sentiment_analysis_results.csv'.")
