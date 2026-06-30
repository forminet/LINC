from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
from pypdf import PdfReader
from database import Documento, crear_tablas, get_db
from entidades import extraer_entidades
import io

app = FastAPI()

crear_tablas()

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
    entidades = extraer_entidades(texto)
    return {
        "id": documento.id,
        "nombre": documento.nombre,
        "paginas": documento.paginas,
        "texto_preview": documento.texto[:300],
        "entidades_encontradas": len(entidades),
        "entidades": entidades[:20]
    }

@app.get("/documentos")
def listar_documentos(db: Session = Depends(get_db)):
    documentos = db.query(Documento).all()
    return [{"id": d.id, "nombre": d.nombre, "paginas": d.paginas} for d in documentos]