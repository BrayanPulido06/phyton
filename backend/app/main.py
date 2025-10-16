"""Endpoints disponibles:
    - GET / : Mensaje de bienvenida
    - POST /api/soportes/ : Crear nuevo soporte
    - GET /api/soportes/ : Listar todos los soportes
    - GET /api/soportes/{id} : Obtener soporte por ID
    - DELETE /api/soportes/{id} : Eliminar soporte
    - POST /api/soportes/upload-excel/ : Cargar datos desde Excel
    - GET /health : Verificar estado de la API
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List
import db
import crud
import excel_crud
from logs import log_info, log_error, log_warning

# Crear instancia de FastAPI
app = FastAPI(
    title="API de Soporte de Mensajería",
    version="1.0.0",
    description="API para gestionar solicitudes de soporte con FastAPI y MySQL"
)

# Configurar CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get(
    "/",
    summary="Página principal",
    description="Retorna mensaje de bienvenida y estado de la API"
)
def read_root():
    try:
        log_info("Acceso a endpoint raíz /")
        return {
            "message": "API de Soporte de Mensajería",
            "status": "OK",
            "version": "1.0.0"
        }
    except Exception as e:
        log_error(f"Error en endpoint raíz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@app.post(
    "/api/soportes/",
    response_model=crud.SoporteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo soporte",
    description="Crea un nuevo registro de soporte en la base de datos"
)
def crear_soporte(soporte: crud.SoporteCreate, db_session: Session = Depends(db.get_db)):

    try:
        log_info(f"Intento de crear soporte - Cédula: {soporte.cedula}")
        
        # Verificar si ya existe un soporte con la misma cédula
        soporte_existente = crud.obtener_soporte_por_cedula(db_session, soporte.cedula)
        
        if soporte_existente:
            log_warning(f"Intento de crear soporte duplicado - Cédula: {soporte.cedula}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un soporte registrado con la cédula {soporte.cedula}"
            )
        
        # Crear el nuevo soporte
        nuevo_soporte = crud.crear_soporte(db_session, soporte)
        
        log_info(f"Soporte creado exitosamente - ID: {nuevo_soporte.id}")
        return nuevo_soporte
        
    except HTTPException:
        raise  # Re-lanzar excepciones HTTP
    except IntegrityError as e:
        log_error(f"Error de integridad al crear soporte: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en los datos. La cédula puede estar duplicada."
        )
    except SQLAlchemyError as e:
        log_error(f"Error de base de datos al crear soporte: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        log_error(f"Error inesperado al crear soporte: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@app.get(
    "/api/soportes/",
    response_model=List[crud.SoporteResponse],
    summary="Listar todos los soportes",
    description="Obtiene una lista paginada de todos los soportes registrados"
)
def listar_soportes(
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(db.get_db)
):

    try:
        log_info(f"Consultando lista de soportes (skip={skip}, limit={limit})")
        
        soportes = crud.obtener_soportes(db_session, skip=skip, limit=limit)
        
        log_info(f"Se retornan {len(soportes)} soportes")
        return soportes
        
    except SQLAlchemyError as e:
        log_error(f"Error de base de datos al listar soportes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        log_error(f"Error inesperado al listar soportes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@app.get(
    "/api/soportes/{soporte_id}",
    response_model=crud.SoporteResponse,
    summary="Obtener soporte por ID",
    description="Obtiene los datos de un soporte específico por su ID"
)
def obtener_soporte(soporte_id: int, db_session: Session = Depends(db.get_db)):

    try:
        log_info(f"Buscando soporte con ID: {soporte_id}")
        
        soporte = crud.obtener_soporte_por_id(db_session, soporte_id)
        
        if not soporte:
            log_warning(f"Soporte no encontrado - ID: {soporte_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró un soporte con ID {soporte_id}"
            )
        
        log_info(f"Soporte encontrado - ID: {soporte_id}")
        return soporte
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        log_error(f"Error de base de datos al obtener soporte: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        log_error(f"Error inesperado al obtener soporte: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@app.delete(
    "/api/soportes/{soporte_id}",
    summary="Eliminar soporte",
    description="Elimina un soporte específico de la base de datos"
)
def eliminar_soporte(soporte_id: int, db_session: Session = Depends(db.get_db)):

    try:
        log_info(f"Intentando eliminar soporte - ID: {soporte_id}")
        
        eliminado = crud.eliminar_soporte(db_session, soporte_id)
        
        if not eliminado:
            log_warning(f"No se puede eliminar - Soporte no encontrado: ID {soporte_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró un soporte con ID {soporte_id}"
            )
        
        log_info(f"Soporte eliminado exitosamente - ID: {soporte_id}")
        return {
            "message": "Soporte eliminado exitosamente",
            "id": soporte_id
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        log_error(f"Error de base de datos al eliminar soporte: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        log_error(f"Error inesperado al eliminar soporte: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@app.post(
    "/api/soportes/upload-excel/",
    summary="Cargar datos desde Excel",
    description="Carga masiva de soportes desde un archivo Excel (máximo 100 registros)"
)
async def upload_excel(
    file: UploadFile = File(...),
    limite: int = 100,
    db_session: Session = Depends(db.get_db)
):
    """
    Returns:
        dict: Resumen de la carga (exitosos, fallidos, errores)
        
    Raises:
        HTTPException 400: Si el archivo no es válido
        HTTPException 500: Si hay error en el servidor
    """
    try:
        log_info(f"Iniciando carga de archivo Excel: {file.filename}")
        
        # Validar tipo de archivo
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser de tipo Excel (.xlsx o .xls)"
            )
        
        # Validar límite
        if limite < 0 or limite > 100:
            limite = 100
        
        # Leer contenido del archivo
        contenido = await file.read()
        
        # Procesar Excel
        df, estadisticas = excel_crud.procesar_excel(contenido, limite)
        
        log_info(f"Excel procesado: {estadisticas['filas_procesadas']} registros")
        
        # Insertar datos en la base de datos
        resultado = excel_crud.insertar_datos_masivos(db_session, df)
        
        log_info(f"Carga completada: {resultado['exitosos']} exitosos, {resultado['fallidos']} fallidos")
        
        return {
            "message": "Proceso de carga completado",
            "archivo": file.filename,
            "estadisticas": estadisticas,
            "resultado": resultado
        }
        
    except ValueError as e:
        log_error(f"Error de validación en archivo Excel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error inesperado al procesar Excel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar archivo: {str(e)}"
        )


@app.get(
    "/health",
    summary="Health check",
    description="Verifica el estado de salud de la API"
)
def health_check():

    try:
        log_info("Health check ejecutado")
        return {
            "status": "healthy",
            "service": "API Soporte",
            "database": "MySQL"
        }
    except Exception as e:
        log_error(f"Error en health check: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )