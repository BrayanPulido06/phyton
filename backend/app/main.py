from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import db
import crud
from logs import log_info, log_error

app = FastAPI(title="API de Soporte", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    log_info("Iniciando aplicación de Soporte")
    db.init_db()
    log_info("Base de datos inicializada")

@app.get("/")
def read_root():
    return {"message": "API de Soporte de Mensajería", "status": "OK"}

@app.post("/api/soportes/", response_model=crud.SoporteResponse, status_code=201)
def crear_soporte(soporte: crud.SoporteCreate, db_session: Session = Depends(db.get_db)):
    try:
        soporte_existente = crud.obtener_soporte_por_cedula(db_session, soporte.cedula)
        if soporte_existente:
            log_error(f"Intento de crear soporte duplicado: {soporte.cedula}")
            raise HTTPException(status_code=400, detail="Ya existe un soporte con esta cédula")
        
        nuevo_soporte = crud.crear_soporte(db_session, soporte)
        return nuevo_soporte
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error al crear soporte: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al crear soporte: {str(e)}")

@app.get("/api/soportes/", response_model=List[crud.SoporteResponse])
def listar_soportes(skip: int = 0, limit: int = 100, db_session: Session = Depends(db.get_db)):
    try:
        soportes = crud.obtener_soportes(db_session, skip=skip, limit=limit)
        return soportes
    except Exception as e:
        log_error(f"Error al listar soportes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al listar soportes: {str(e)}")

@app.get("/api/soportes/{soporte_id}", response_model=crud.SoporteResponse)
def obtener_soporte(soporte_id: int, db_session: Session = Depends(db.get_db)):
    try:
        soporte = crud.obtener_soporte_por_id(db_session, soporte_id)
        if not soporte:
            raise HTTPException(status_code=404, detail="Soporte no encontrado")
        return soporte
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error al obtener soporte: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener soporte: {str(e)}")

@app.delete("/api/soportes/{soporte_id}")
def eliminar_soporte(soporte_id: int, db_session: Session = Depends(db.get_db)):
    try:
        eliminado = crud.eliminar_soporte(db_session, soporte_id)
        if not eliminado:
            raise HTTPException(status_code=404, detail="Soporte no encontrado")
        return {"message": "Soporte eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error al eliminar soporte: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar soporte: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy"}