from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
from pypdf import PdfReader
from database import Documento, crear_tablas, get_db
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
    return {
        "id": documento.id,
        "nombre": documento.nombre,
        "paginas": documento.paginas,
        "texto": documento.texto[:500]
    }

@app.get("/documentos")
def listar_documentos(db: Session = Depends(get_db)):
    documentos = db.query(Documento).all()
    return documentos