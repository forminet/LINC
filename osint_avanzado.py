import requests
from datetime import datetime

def buscar_noticias_google(tema: str):
    """Busca noticias reales usando NewsAPI"""
    try:
        api_key = "8cbe1015110a403e9a8439f338d0f6aa"
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": tema,
            "language": "es",
            "sortBy": "publishedAt",
            "pageSize": 10,
            "apiKey": api_key
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        noticias = []
        if data.get("articles"):
            for article in data["articles"][:10]:
                noticias.append({
                    "titulo": article.get("title", "Sin título"),
                    "descripcion": article.get("description", "")[:200],
                    "url": article.get("url", ""),
                    "fuente": article.get("source", {}).get("name", "NewsAPI"),
                    "fecha": article.get("publishedAt", datetime.utcnow().isoformat()),
                    "imagen": article.get("urlToImage", ""),
                    "categoria": "general"
                })
        
        return noticias
    except requests.exceptions.RequestException as e:
        print(f"Error NewsAPI: {e}")
        return []
    except Exception as e:
        print(f"Error inesperado: {e}")
        return []

def recopilar_osint_avanzado(terminos: list):
    """Recopila noticias reales para una lista de términos"""
    resultado = {}
    for termino in terminos[:3]:
        resultado[termino] = buscar_noticias_google(termino)
    return resultado