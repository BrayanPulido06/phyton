from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List
import io
from sqlalchemy.orm import Session
import crud
import db
from logs import log_info, log_error
from export_utils import generate_excel, generate_pdf

# ============= CREAR INSTANCIA DE FASTAPI =============
app = FastAPI(
    title="API de Soporte de Personas",
    version="1.0.0",
    description="API para gestionar solicitudes de soporte con FastAPI y MySQL"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:89"],  # Ajusta esto según la URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= EVENTOS DE INICIO =============
@app.on_event("startup")
def startup_event():
    try:
        log_info("=== Iniciando aplicación de Soporte ===")
        
        # Inicializar base de datos
        resultado = db.init_db()
        
        if resultado:
            log_info("Base de datos MySQL inicializada correctamente")
        else:
            log_error("Error al inicializar la base de datos")
            
    except Exception as e:
        log_error(f"Error crítico al iniciar aplicación: {str(e)}")
        raise

@app.get("/api/soportes/export/excel")
def export_soportes_excel(db_session: Session = Depends(db.get_db)):
    try:
        soportes = crud.obtener_soportes(db_session)
        soportes_dict = [soporte.__dict__ for soporte in soportes]
        for soporte in soportes_dict:
            soporte.pop('_sa_instance_state', None)
        excel_file = generate_excel(soportes_dict)
        return StreamingResponse(
            io.BytesIO(excel_file.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=soportes.xlsx"}
        )
    except Exception as e:
        log_error(f"Error al exportar a Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/soportes/export/pdf")
def export_soportes_pdf(db_session: Session = Depends(db.get_db)):
    try:
        soportes = crud.obtener_soportes(db_session)
        soportes_dict = [soporte.__dict__ for soporte in soportes]
        for soporte in soportes_dict:
            soporte.pop('_sa_instance_state', None)
        pdf_file = generate_pdf(soportes_dict)
        return StreamingResponse(
            io.BytesIO(pdf_file.getvalue()),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=soportes.pdf"}
        )
    except Exception as e:
        log_error(f"Error al exportar a PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/soportes/", response_model=List[crud.SoporteResponse])
def get_soportes(skip: int = 0, limit: int = 100, db: Session = Depends(db.get_db)):
    try:
        soportes = crud.obtener_soportes(db, skip=skip, limit=limit)
        return soportes
    except Exception as e:
        log_error(f"Error al obtener soportes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# ... (resto del código)

