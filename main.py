from fastapi import FastAPI, UploadFile, File
from pypdf import PdfReader
import io

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensaje": "LINC esta vivo"}

@app.post("/subir-pdf")
async def subir_pdf(archivo: UploadFile = File(...)):
    contenido = await archivo.read()
    lector = PdfReader(io.BytesIO(contenido))
    texto = ""
    for pagina in lector.pages:
        texto += pagina.extract_text()
    return {
        "nombre": archivo.filename,
        "paginas": len(lector.pages),
        "texto": texto[:500]
    }