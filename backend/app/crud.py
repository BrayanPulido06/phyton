from sqlalchemy.orm import Session
from db import Soporte
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from logs import log_info, log_error

class SoporteCreate(BaseModel):
    nombre: str
    direccion: str
    cedula: str

class SoporteResponse(BaseModel):
    id: int
    nombre: str
    direccion: str
    cedula: str
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True

def crear_soporte(db: Session, soporte: SoporteCreate) -> Soporte:
    try:
        db_soporte = Soporte(
            nombre=soporte.nombre,
            direccion=soporte.direccion,
            cedula=soporte.cedula
        )
        db.add(db_soporte)
        db.commit()
        db.refresh(db_soporte)
        log_info(f"Soporte creado: {soporte.cedula} - {soporte.nombre}")
        return db_soporte
    except Exception as e:
        db.rollback()
        log_error(f"Error al crear soporte: {str(e)}")
        raise e

def obtener_soportes(db: Session, skip: int = 0, limit: int = 100) -> List[Soporte]:
    try:
        soportes = db.query(Soporte).offset(skip).limit(limit).all()
        log_info(f"Consultados {len(soportes)} soportes")
        return soportes
    except Exception as e:
        log_error(f"Error al obtener soportes: {str(e)}")
        raise e

def obtener_soporte_por_id(db: Session, soporte_id: int) -> Optional[Soporte]:
    try:
        soporte = db.query(Soporte).filter(Soporte.id == soporte_id).first()
        if soporte:
            log_info(f"Soporte encontrado: ID {soporte_id}")
        else:
            log_info(f"Soporte no encontrado: ID {soporte_id}")
        return soporte
    except Exception as e:
        log_error(f"Error al obtener soporte por ID: {str(e)}")
        raise e

def obtener_soporte_por_cedula(db: Session, cedula: str) -> Optional[Soporte]:
    try:
        soporte = db.query(Soporte).filter(Soporte.cedula == cedula).first()
        return soporte
    except Exception as e:
        log_error(f"Error al buscar soporte por cédula: {str(e)}")
        raise e

def eliminar_soporte(db: Session, soporte_id: int) -> bool:
    try:
        soporte = db.query(Soporte).filter(Soporte.id == soporte_id).first()
        if soporte:
            db.delete(soporte)
            db.commit()
            log_info(f"Soporte eliminado: ID {soporte_id}")
            return True
        log_info(f"Soporte no encontrado para eliminar: ID {soporte_id}")
        return False
    except Exception as e:
        db.rollback()
        log_error(f"Error al eliminar soporte: {str(e)}")
        raise e