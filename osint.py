import requests
from bs4 import BeautifulSoup
from datetime import datetime

def buscar_noticias(palabra_clave: str):
    """Busca noticias sobre una palabra clave usando NewsAPI"""
    try:
        url = f"https://newsapi.org/v2/everything?q={palabra_clave}&language=es&sortBy=publishedAt&pageSize=5"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            articulos = []
            for art in data.get("articles", [])[:5]:
                articulos.append({
                    "titulo": art.get("title"),
                    "descripcion": art.get("description"),
                    "url": art.get("url"),
                    "fecha": art.get("publishedAt")
                })
            return articulos
        return []
    except:
        return []

def buscar_google(consulta: str):
    """Busca en Google (básico, sin API key)"""
    try:
        url = "https://www.google.com/search"
        params = {"q": consulta}
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, params=params, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, "html.parser")
        resultados = []
        for g in soup.find_all("div", class_="g")[:3]:
            try:
                titulo = g.find("h3").text
                link = g.find("a")["href"]
                resultados.append({"titulo": titulo, "url": link})
            except:
                pass
        return resultados
    except:
        return []

def recopilar_osint(terminos: list):
    """Recopila información OSINT sobre una lista de términos"""
    resultado = {}
    for termino in terminos[:5]:  # Máximo 5 términos
        resultado[termino] = {
            "noticias": buscar_noticias(termino),
            "busquedas": buscar_google(termino)
        }
    return resultado