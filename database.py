from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./linc.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Documento(Base):
    __tablename__ = "documentos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    paginas = Column(Integer)
    texto = Column(Text)
    categoria = Column(String, default="general")  # politica, economia, belico, social
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    entidades = relationship("Entidad", back_populates="documento")

class Entidad(Base):
    __tablename__ = "entidades"
    id = Column(Integer, primary_key=True, index=True)
    texto = Column(String, index=True)
    tipo = Column(String)  # PER, ORG, LOC, MISC
    documento_id = Column(Integer, ForeignKey("documentos.id"))
    documento = relationship("Documento", back_populates="entidades")

class Evento(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    descripcion = Column(Text)
    categoria = Column(String)  # politica, economia, belico, social
    fecha = Column(DateTime, default=datetime.utcnow)
    latitud = Column(String)
    longitud = Column(String)
    severidad = Column(Integer)  # 1-5

def crear_tablas():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()