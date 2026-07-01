from whoosh import index
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.qparser import QueryParser
import os

DIRECTORIO_INDICE = "indice_busqueda"

schema = Schema(
    doc_id=ID(stored=True),
    nombre=TEXT(stored=True),
    texto=TEXT(stored=True)
)

def crear_indice():
    if not os.path.exists(DIRECTORIO_INDICE):
        os.mkdir(DIRECTORIO_INDICE)
        index.create_in(DIRECTORIO_INDICE, schema)

def agregar_documento(doc_id: int, nombre: str, texto: str):
    ix = index.open_dir(DIRECTORIO_INDICE)
    writer = ix.writer()
    writer.add_document(doc_id=str(doc_id), nombre=nombre, texto=texto)
    writer.commit()

def buscar(consulta: str):
    ix = index.open_dir(DIRECTORIO_INDICE)
    resultados_encontrados = []
    with ix.searcher() as searcher:
        query = QueryParser("texto", ix.schema).parse(consulta)
        resultados = searcher.search(query, limit=10)
        for r in resultados:
            resultados_encontrados.append({
                "doc_id": r["doc_id"],
                "nombre": r["nombre"],
                "fragmento": r.highlights("texto") or "Sin preview"
            })
    return resultados_encontrados