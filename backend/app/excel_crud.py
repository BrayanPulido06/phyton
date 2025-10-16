import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from db import Soporte
from typing import List, Dict, Tuple
from io import BytesIO
from logs import log_info, log_error, log_warning


def validar_columnas_excel(df: pd.DataFrame) -> Tuple[bool, str]:
    columnas_requeridas = {'nombre', 'cedula', 'direccion'}
    columnas_df = set(df.columns.str.lower().str.strip())
    
    if not columnas_requeridas.issubset(columnas_df):
        faltantes = columnas_requeridas - columnas_df
        return False, f"Columnas faltantes: {', '.join(faltantes)}"
    
    return True, ""


def limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    # Normalizar nombres de columnas
    df.columns = df.columns.str.lower().str.strip()
    
    # Eliminar filas completamente vacías
    df = df.dropna(how='all')
    
    # Eliminar espacios en blanco extras
    for col in ['nombre', 'cedula', 'direccion']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # Eliminar filas donde falten datos críticos
    df = df.dropna(subset=['nombre', 'cedula', 'direccion'])
    
    # Eliminar duplicados basados en cédula
    df = df.drop_duplicates(subset=['cedula'], keep='first')
    
    return df


def procesar_excel(archivo_bytes: bytes, limite: int = 100) -> Tuple[pd.DataFrame, Dict[str, any]]:

    try:
        log_info("Iniciando procesamiento de archivo Excel")
        
        # Leer archivo Excel
        df = pd.read_excel(BytesIO(archivo_bytes), engine='openpyxl')
        
        log_info(f"Archivo Excel leído: {len(df)} filas encontradas")
        
        # Validar que no esté vacío
        if df.empty:
            raise ValueError("El archivo Excel está vacío")
        
        # Validar columnas
        es_valido, mensaje = validar_columnas_excel(df)
        if not es_valido:
            raise ValueError(mensaje)
        
        # Limpiar datos
        df = limpiar_dataframe(df)
        
        # Aplicar límite
        if limite > 0:
            df = df.head(min(limite, 100))
        else:
            df = df.head(100)
        
        estadisticas = {
            "filas_procesadas": len(df),
            "columnas": list(df.columns)
        }
        
        log_info(f"Excel procesado exitosamente: {len(df)} registros válidos")
        
        return df, estadisticas
        
    except Exception as e:
        log_error(f"Error al procesar archivo Excel: {str(e)}")
        raise ValueError(f"Error al procesar archivo Excel: {str(e)}")


def insertar_datos_masivos(db: Session, df: pd.DataFrame) -> Dict[str, any]:

    exitosos = 0
    fallidos = 0
    errores = []
    
    log_info(f"Iniciando inserción masiva de {len(df)} registros")
    
    for index, row in df.iterrows():
        try:
            # Validar que los datos cumplan requisitos mínimos
            nombre = str(row['nombre']).strip()
            cedula = str(row['cedula']).strip()
            direccion = str(row['direccion']).strip()
            
            if len(nombre) < 3:
                raise ValueError("Nombre debe tener al menos 3 caracteres")
            if len(cedula) < 5:
                raise ValueError("Cédula debe tener al menos 5 caracteres")
            if len(direccion) < 5:
                raise ValueError("Dirección debe tener al menos 5 caracteres")
            
            # Verificar si ya existe
            existe = db.query(Soporte).filter(Soporte.cedula == cedula).first()
            
            if existe:
                log_warning(f"Cédula duplicada (fila {index + 2}): {cedula}")
                errores.append({
                    "fila": index + 2,
                    "cedula": cedula,
                    "error": "Cédula ya existe en la base de datos"
                })
                fallidos += 1
                continue
            
            # Crear nuevo registro
            nuevo_soporte = Soporte(
                nombre=nombre,
                cedula=cedula,
                direccion=direccion
            )
            
            db.add(nuevo_soporte)
            db.flush()  # Flush para detectar errores antes del commit final
            
            exitosos += 1
            log_info(f"Registro insertado (fila {index + 2}): {cedula}")
            
        except IntegrityError as e:
            db.rollback()
            log_error(f"Error de integridad en fila {index + 2}: {str(e)}")
            errores.append({
                "fila": index + 2,
                "cedula": row.get('cedula', 'N/A'),
                "error": "Error de integridad (posible duplicado)"
            })
            fallidos += 1
            
        except ValueError as e:
            log_error(f"Error de validación en fila {index + 2}: {str(e)}")
            errores.append({
                "fila": index + 2,
                "cedula": row.get('cedula', 'N/A'),
                "error": str(e)
            })
            fallidos += 1
            
        except Exception as e:
            log_error(f"Error inesperado en fila {index + 2}: {str(e)}")
            errores.append({
                "fila": index + 2,
                "cedula": row.get('cedula', 'N/A'),
                "error": f"Error inesperado: {str(e)}"
            })
            fallidos += 1
    
    # Commit final si hubo registros exitosos
    try:
        if exitosos > 0:
            db.commit()
            log_info(f"Inserción masiva completada: {exitosos} exitosos, {fallidos} fallidos")
        else:
            db.rollback()
            log_warning("No se insertó ningún registro")
    except Exception as e:
        db.rollback()
        log_error(f"Error al hacer commit final: {str(e)}")
        raise
    
    return {
        "total_procesados": len(df),
        "exitosos": exitosos,
        "fallidos": fallidos,
        "errores": errores[:10]  # Limitar a 10 errores para no sobrecargar respuesta
    }