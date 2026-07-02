from datetime import datetime

def buscar_noticias_google(tema: str):
    """Devuelve noticias simuladas como placeholder"""
    try:
        noticias = [
            {
                "titulo": f"Noticia sobre {tema} - Fuente 1",
                "url": "https://news.google.com",
                "fuente": "Google News",
                "fecha": datetime.utcnow().isoformat(),
                "categoria": "general"
            },
            {
                "titulo": f"Actualización: {tema}",
                "url": "https://news.google.com",
                "fuente": "Google News",
                "fecha": datetime.utcnow().isoformat(),
                "categoria": "general"
            }
        ]
        return noticias
    except Exception as e:
        print(f"Error: {e}")
        return []

def recopilar_osint_avanzado(terminos: list):
    """Recopila noticias para una lista de términos"""
    resultado = {}
    for termino in terminos[:3]:
        resultado[termino] = buscar_noticias_google(termino)
    return resultado