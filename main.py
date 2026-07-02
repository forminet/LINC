from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pypdf import PdfReader
from database import Documento, Entidad, Evento, crear_tablas, get_db
from buscador import crear_indice, agregar_documento, buscar
import io
import os
from datetime import datetime

app = FastAPI()

crear_tablas()
crear_indice()

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

CATEGORIAS = ["politica", "economia", "belico", "social"]

@app.get("/")
def inicio():
    return {"mensaje": "LINC esta vivo"}

@app.post("/subir-pdf")
async def subir_pdf(archivo: UploadFile = File(...), categoria: str = "general", db: Session = Depends(get_db)):
    contenido = await archivo.read()
    lector = PdfReader(io.BytesIO(contenido))
    texto = ""
    for pagina in lector.pages:
        texto += pagina.extract_text()
    documento = Documento(
        nombre=archivo.filename,
        paginas=len(lector.pages),
        texto=texto,
        categoria=categoria if categoria in CATEGORIAS else "general"
    )
    db.add(documento)
    db.commit()
    db.refresh(documento)
    agregar_documento(documento.id, documento.nombre, texto)
    return {
        "id": documento.id,
        "nombre": documento.nombre,
        "paginas": documento.paginas,
        "categoria": documento.categoria,
        "entidades_guardadas": 0
    }

@app.get("/documentos")
def listar_documentos(categoria: str = None, db: Session = Depends(get_db)):
    query = db.query(Documento)
    if categoria and categoria in CATEGORIAS:
        query = query.filter(Documento.categoria == categoria)
    documentos = query.all()
    return [{"id": d.id, "nombre": d.nombre, "paginas": d.paginas, "categoria": d.categoria, "total_entidades": len(d.entidades)} for d in documentos]

@app.get("/documentos/{id}/entidades")
def ver_entidades(id: int, db: Session = Depends(get_db)):
    entidades = db.query(Entidad).filter(Entidad.documento_id == id).all()
    return [{"texto": e.texto, "tipo": e.tipo} for e in entidades]

@app.get("/buscar")
def buscar_documentos(q: str):
    resultados = buscar(q)
    return resultados

@app.delete("/documentos/{id}")
def eliminar_documento(id: int, db: Session = Depends(get_db)):
    documento = db.query(Documento).filter(Documento.id == id).first()
    if not documento:
        return {"error": "Documento no encontrado"}
    db.query(Entidad).filter(Entidad.documento_id == id).delete()
    db.delete(documento)
    db.commit()
    return {"mensaje": f"Documento {id} eliminado"}

@app.get("/estadisticas")
def estadisticas(db: Session = Depends(get_db)):
    total_docs = db.query(Documento).count()
    total_entidades = db.query(Entidad).count()
    por_tipo = {}
    por_categoria = {}
    entidades = db.query(Entidad).all()
    documentos = db.query(Documento).all()
    
    for e in entidades:
        por_tipo[e.tipo] = por_tipo.get(e.tipo, 0) + 1
    for d in documentos:
        por_categoria[d.categoria] = por_categoria.get(d.categoria, 0) + 1
    
    return {
        "total_documentos": total_docs,
        "total_entidades": total_entidades,
        "por_tipo": por_tipo,
        "por_categoria": por_categoria
    }

@app.post("/eventos")
def crear_evento(titulo: str, descripcion: str, categoria: str, latitud: str, longitud: str, severidad: int = 1, db: Session = Depends(get_db)):
    evento = Evento(
        titulo=titulo,
        descripcion=descripcion,
        categoria=categoria if categoria in CATEGORIAS else "general",
        latitud=latitud,
        longitud=longitud,
        severidad=min(severidad, 5)
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return {"id": evento.id, "titulo": evento.titulo, "categoria": evento.categoria}

@app.get("/eventos")
def listar_eventos(categoria: str = None, db: Session = Depends(get_db)):
    query = db.query(Evento)
    if categoria and categoria in CATEGORIAS:
        query = query.filter(Evento.categoria == categoria)
    eventos = query.order_by(Evento.fecha.desc()).all()
    return [{"id": e.id, "titulo": e.titulo, "descripcion": e.descripcion, "categoria": e.categoria, "fecha": e.fecha.isoformat(), "latitud": e.latitud, "longitud": e.longitud, "severidad": e.severidad} for e in eventos]

@app.get("/categorias")
def get_categorias():
    return {"categorias": CATEGORIAS}

@app.get("/noticias")
def obtener_noticias(tema: str):
    from osint_avanzado import buscar_noticias_google
    noticias = buscar_noticias_google(tema)
    return {"tema": tema, "cantidad": len(noticias), "noticias": noticias}