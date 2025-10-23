"""Endpoints disponibles:
    - GET / : Mensaje de bienvenida
    - POST /api/auth/login : Login de usuario
    - GET /api/auth/me : Información del usuario actual
    - POST /api/soportes/ : Crear nuevo soporte
    - GET /api/soportes/ : Listar todos los soportes
    - GET /api/soportes/{id} : Obtener soporte por ID
    - DELETE /api/soportes/{id} : Eliminar soporte
    - POST /api/soportes/upload-excel/ : Cargar datos desde Excel
    - GET /health : Verificar estado de la API
"""

import io
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import jwt
from passlib.context import CryptContext
import db
import crud
import excel_crud
from logs import log_info, log_error, log_warning
from export_utils import generate_excel, generate_pdf

# ============= CONFIGURACIÓN DE AUTENTICACIÓN =============
SECRET_KEY = "tu_clave_secreta_super_segura_cambiala_en_produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# ============= MODELOS DE AUTENTICACIÓN =============
class User(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenData(BaseModel):
    username: Optional[str] = None

# Base de datos de usuarios (cambiar por BD real en producción)
fake_users_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@soporte.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "usuario": {
        "id": 2,
        "username": "usuario",
        "email": "usuario@soporte.com",
        "hashed_password": "$2b$12$5JZE.8QqVFZKZb7DCxKpFO7H5H5H5H5H5H5H5H5H5H5H5H5H5H5",
        "disabled": False,
    }
}

# ============= FUNCIONES DE AUTENTICACIÓN =============
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[UserInDB]:
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return User(
        id=user.id,
        username=user.username,
        email=user.email,
        disabled=user.disabled
    )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

# ============= CREAR INSTANCIA DE FASTAPI =============
app = FastAPI(
    title="API de Soporte de Personas",
    version="1.0.0",
    description="API para gestionar solicitudes de soporte con FastAPI y MySQL"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# ============= ENDPOINTS DE AUTENTICACIÓN =============
@app.post(
    "/api/auth/login",
    response_model=Token,
    summary="Iniciar sesión",
    description="Autenticar usuario y obtener token JWT"
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        log_info(f"Intento de login - Usuario: {form_data.username}")
        
        user = authenticate_user(form_data.username, form_data.password)
        
        if not user:
            log_warning(f"Login fallido - Usuario: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        
        log_info(f"Login exitoso - Usuario: {form_data.username}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=User(
                id=user.id,
                username=user.username,
                email=user.email,
                disabled=user.disabled
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@app.get(
    "/api/auth/me",
    response_model=User,
    summary="Información del usuario",
    description="Obtener información del usuario autenticado"
)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    log_info(f"Usuario consultó su información: {current_user.username}")
    return current_user

@app.post(
    "/api/auth/logout",
    summary="Cerrar sesión",
    description="Cerrar sesión del usuario"
)
async def logout(current_user: User = Depends(get_current_active_user)):
    log_info(f"Usuario cerró sesión: {current_user.username}")
    return {"message": "Sesión cerrada exitosamente"}

# ============= ENDPOINT RAÍZ =============
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
            "version": "1.0.0",
            "endpoints": {
                "docs": "/docs",
                "auth": "/api/auth",
                "soportes": "/api/soportes"
            }
        }
    except Exception as e:
        log_error(f"Error en endpoint raíz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# ============= ENDPOINTS DE SOPORTES (TUS ENDPOINTS EXISTENTES) =============

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
        
        soporte_existente = crud.obtener_soporte_por_cedula(db_session, soporte.cedula)
        
        if soporte_existente:
            log_warning(f"Intento de crear soporte duplicado - Cédula: {soporte.cedula}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un soporte registrado con la cédula {soporte.cedula}"
            )
        
        nuevo_soporte = crud.crear_soporte(db_session, soporte)
        
        log_info(f"Soporte creado exitosamente - ID: {nuevo_soporte.id}")
        return nuevo_soporte
        
    except HTTPException:
        raise
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
    try:
        log_info(f"Iniciando carga de archivo Excel: {file.filename}")
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser de tipo Excel (.xlsx o .xls)"
            )
        
        if limite < 0 or limite > 100:
            limite = 100
        
        contenido = await file.read()
        
        df, estadisticas = excel_crud.procesar_excel(contenido, limite)
        
        log_info(f"Excel procesado: {estadisticas['filas_procesadas']} registros")
        
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
