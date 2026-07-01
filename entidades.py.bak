import spacy

nlp = spacy.load("es_core_news_sm")

def extraer_entidades(texto: str):
    doc = nlp(texto)
    entidades = []
    for ent in doc.ents:
        entidades.append({
            "texto": ent.text,
            "tipo": ent.label_
        })
    return entidades
