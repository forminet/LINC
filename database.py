from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

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
    entidades = relationship("Entidad", back_populates="documento")

class Entidad(Base):
    __tablename__ = "entidades"
    id = Column(Integer, primary_key=True, index=True)
    texto = Column(String, index=True)
    tipo = Column(String)
    documento_id = Column(Integer, ForeignKey("documentos.id"))
    documento = relationship("Documento", back_populates="entidades")

def crear_tablas():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()