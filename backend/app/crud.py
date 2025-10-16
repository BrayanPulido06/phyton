from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from db import Soporte
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from logs import log_info, log_error, log_warning


class SoporteCreate(BaseModel):

    nombre: str = Field(..., min_length=3, description="Nombre completo")
    direccion: str = Field(..., min_length=5, description="Dirección completa")
    cedula: str = Field(..., min_length=5, description="Número de cédula")


class SoporteResponse(BaseModel):

    id: int
    nombre: str
    direccion: str
    cedula: str
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True


def crear_soporte(db: Session, soporte: SoporteCreate) -> Optional[Soporte]:

    db_soporte = None
    try:
        # Crear instancia del modelo
        db_soporte = Soporte(
            nombre=soporte.nombre,
            direccion=soporte.direccion,
            cedula=soporte.cedula
        )
        
        # Agregar a la sesión
        db.add(db_soporte)
        
        # Confirmar cambios
        db.commit()
        
        # Refrescar objeto con datos de la DB
        db.refresh(db_soporte)
        
        log_info(f"Soporte creado exitosamente - Cédula: {soporte.cedula}, Nombre: {soporte.nombre}")
        return db_soporte
        
    except IntegrityError as e:
        db.rollback()
        log_error(f"Error de integridad al crear soporte - Cédula duplicada: {soporte.cedula}")
        raise
    except SQLAlchemyError as e:
        db.rollback()
        log_error(f"Error de base de datos al crear soporte: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        log_error(f"Error inesperado al crear soporte: {str(e)}")
        raise


def obtener_soportes(db: Session, skip: int = 0, limit: int = 100) -> List[Soporte]:

    try:
        # Consultar todos los soportes con paginación
        soportes = db.query(Soporte)\
            .order_by(Soporte.fecha_creacion.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        log_info(f"Consultados {len(soportes)} soportes (skip={skip}, limit={limit})")
        return soportes
        
    except SQLAlchemyError as e:
        log_error(f"Error al obtener lista de soportes: {str(e)}")
        raise
    except Exception as e:
        log_error(f"Error inesperado al obtener soportes: {str(e)}")
        raise


def obtener_soporte_por_id(db: Session, soporte_id: int) -> Optional[Soporte]:

    try:
        # Buscar soporte por ID
        soporte = db.query(Soporte).filter(Soporte.id == soporte_id).first()
        
        if soporte:
            log_info(f"Soporte encontrado - ID: {soporte_id}")
        else:
            log_warning(f"Soporte no encontrado - ID: {soporte_id}")
            
        return soporte
        
    except SQLAlchemyError as e:
        log_error(f"Error al buscar soporte por ID {soporte_id}: {str(e)}")
        raise
    except Exception as e:
        log_error(f"Error inesperado al buscar soporte por ID: {str(e)}")
        raise


def obtener_soporte_por_cedula(db: Session, cedula: str) -> Optional[Soporte]:

    try:
        # Buscar soporte por cédula
        soporte = db.query(Soporte).filter(Soporte.cedula == cedula).first()
        
        if soporte:
            log_info(f"Soporte encontrado - Cédula: {cedula}")
        else:
            log_info(f"No existe soporte con cédula: {cedula}")
            
        return soporte
        
    except SQLAlchemyError as e:
        log_error(f"Error al buscar soporte por cédula {cedula}: {str(e)}")
        raise
    except Exception as e:
        log_error(f"Error inesperado al buscar soporte por cédula: {str(e)}")
        raise


def eliminar_soporte(db: Session, soporte_id: int) -> bool:

    try:
        # Buscar soporte
        soporte = db.query(Soporte).filter(Soporte.id == soporte_id).first()
        
        if not soporte:
            log_warning(f"No se puede eliminar - Soporte no encontrado: ID {soporte_id}")
            return False
        
        # Eliminar soporte
        db.delete(soporte)
        db.commit()
        
        log_info(f"Soporte eliminado exitosamente - ID: {soporte_id}")
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        log_error(f"Error al eliminar soporte ID {soporte_id}: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        log_error(f"Error inesperado al eliminar soporte: {str(e)}")
        raise