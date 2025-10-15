"""
Módulo de configuración de base de datos MySQL.
Gestiona la conexión con MySQL y define los modelos de datos.
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from logs import log_info, log_error

# Obtener URL de base de datos desde variables de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://admin:admin123@db:3306/soporte_db"
)

# Crear motor de base de datos
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usar
    pool_recycle=3600    # Recicla conexiones cada hora
)

# Crear fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para modelos
Base = declarative_base()


class Soporte(Base):
    """
    Modelo de datos para la tabla 'soportes'.
    
    Atributos:
        id (int): Identificador único auto-incremental
        nombre (str): Nombre completo de la persona
        direccion (str): Dirección completa
        cedula (str): Número de cédula (único)
        fecha_creacion (datetime): Fecha y hora de creación del registro
    """
    __tablename__ = "soportes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    direccion = Column(String(500), nullable=False)
    cedula = Column(String(50), unique=True, nullable=False, index=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)


def get_db():
    """
    Generador que proporciona sesiones de base de datos.
    
    Yields:
        Session: Sesión de SQLAlchemy para realizar operaciones
        
    Note:
        Cierra automáticamente la conexión al terminar usando 'finally'
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        log_error(f"Error en sesión de base de datos: {str(e)}")
        raise
    finally:
        # Cerrar conexión correctamente
        if db:
            db.close()
            log_info("Conexión a base de datos cerrada correctamente")


def init_db():
    """
    Inicializa la base de datos creando todas las tablas definidas.
    
    Returns:
        bool: True si se inicializó correctamente, False en caso de error
        
    Note:
        Esta función se ejecuta al iniciar la aplicación
    """
    try:
        Base.metadata.create_all(bind=engine)
        log_info("Base de datos MySQL inicializada correctamente")
        return True
    except Exception as e:
        log_error(f"Error al inicializar base de datos: {str(e)}")
        return False