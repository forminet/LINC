from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pypdf import PdfReader
from database import Documento, Entidad, crear_tablas, get_db
# from entidades import extraer_entidades
from buscador import crear_indice, agregar_documento, buscar
import io
import os

app = FastAPI()

crear_tablas()
crear_indice()

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def inicio():
    return {"mensaje": "LINC esta vivo"}

@app.post("/subir-pdf")
async def subir_pdf(archivo: UploadFile = File(...), db: Session = Depends(get_db)):
    contenido = await archivo.read()
    lector = PdfReader(io.BytesIO(contenido))
    texto = ""
    for pagina in lector.pages:
        texto += pagina.extract_text()
    documento = Documento(
        nombre=archivo.filename,
        paginas=len(lector.pages),
        texto=texto
    )
    db.add(documento)
    db.commit()
    db.refresh(documento)
    # Extraccion de entidades deshabilitada temporalmente en esta máquina
    entidades_extraidas = []
    agregar_documento(documento.id, documento.nombre, texto) # type: ignore
    return {
        "id": documento.id,
        "nombre": documento.nombre,
        "paginas": documento.paginas,
        "entidades_guardadas": len(entidades_extraidas)
    }

@app.get("/documentos")
def listar_documentos(db: Session = Depends(get_db)):
    documentos = db.query(Documento).all()
    return [{"id": d.id, "nombre": d.nombre, "paginas": d.paginas, "total_entidades": len(d.entidades)} for d in documentos]

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
    return {"mensaje": f"Documento {id} eliminado correctamente"}

@app.get("/estadisticas")
def estadisticas(db: Session = Depends(get_db)):
    total_docs = db.query(Documento).count()
    total_entidades = db.query(Entidad).count()
    por_tipo = {}
    entidades = db.query(Entidad).all()
    for e in entidades:
        por_tipo[e.tipo] = por_tipo.get(e.tipo, 0) + 1
    return {
        "total_documentos": total_docs,
        "total_entidades": total_entidades,
        "por_tipo": por_tipo
    }
@app.get("/osint")
def obtener_osint(terminos: str):
    """Recopila información OSINT sobre términos separados por comas"""
    from osint import recopilar_osint
    lista_terminos = [t.strip() for t in terminos.split(",")]
    resultado = recopilar_osint(lista_terminos)
    return resultado