from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import pytz
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos desde variables de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://user:password@db:3306/soporte"
)

# Crear motor de base de datos
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


def get_colombia_time():

    bogota_tz = pytz.timezone('America/Bogota')
    return datetime.now(bogota_tz)


class Soporte(Base):

    __tablename__ = "soportes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(255), nullable=False, index=True)
    cedula = Column(String(20), nullable=False, unique=True, index=True)
    direccion = Column(Text, nullable=False)
    fecha_creacion = Column(DateTime, default=get_colombia_time, nullable=False)

    def __repr__(self):
        return f"<Soporte(id={self.id}, nombre='{self.nombre}', cedula='{self.cedula}')>"


def init_db():

    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente en MySQL")
        return True
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        return False


def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()