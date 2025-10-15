"""
Sistema de logging para la aplicación.
Maneja el registro de eventos, errores y advertencias en archivo y consola.

El sistema crea automáticamente:
    - Carpeta 'logs' si no existe
    - Archivo de log diario con formato: soporte_YYYYMMDD.log
"""

import logging
from datetime import datetime
import os
from pathlib import Path


def configurar_logging():
    """
    Configura el sistema de logging de la aplicación.
    
    Returns:
        logging.Logger: Logger configurado
        
    Note:
        Crea la carpeta 'logs' si no existe y configura:
        - Nivel de logging: INFO
        - Formato: timestamp - nombre - nivel - mensaje
        - Salidas: archivo diario y consola
    """
    try:
        # Crear directorio de logs si no existe
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Nombre del archivo con fecha actual
        fecha_actual = datetime.now().strftime('%Y%m%d')
        log_file = log_dir / f"soporte_{fecha_actual}.log"
        
        # Configurar formato de logs
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt=date_format,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger("SoporteApp")
        logger.info(f"Sistema de logging inicializado - Archivo: {log_file}")
        
        return logger
        
    except Exception as e:
        print(f"Error al configurar logging: {str(e)}")
        raise


# Inicializar logger
logger = configurar_logging()


def log_info(message: str):
    """
    Registra un mensaje informativo.
    
    Args:
        message (str): Mensaje a registrar
        
    Returns:
        None
        
    Example:
        log_info("Usuario creado exitosamente")
    """
    try:
        logger.info(message)
    except Exception as e:
        print(f"Error al registrar info: {str(e)}")


def log_error(message: str):
    """
    Registra un mensaje de error.
    
    Args:
        message (str): Mensaje de error a registrar
        
    Returns:
        None
        
    Example:
        log_error("Error al conectar con la base de datos")
    """
    try:
        logger.error(message)
    except Exception as e:
        print(f"Error al registrar error: {str(e)}")


def log_warning(message: str):
    """
    Registra un mensaje de advertencia.
    
    Args:
        message (str): Mensaje de advertencia a registrar
        
    Returns:
        None
        
    Example:
        log_warning("Intento de acceso con credenciales inválidas")
    """
    try:
        logger.warning(message)
    except Exception as e:
        print(f"Error al registrar warning: {str(e)}")


def log_debug(message: str):
    """
    Registra un mensaje de depuración.
    
    Args:
        message (str): Mensaje de debug a registrar
        
    Returns:
        None
        
    Note:
        Solo se muestra si el nivel de logging está en DEBUG
        
    Example:
        log_debug("Valor de variable x: 123")
    """
    try:
        logger.debug(message)
    except Exception as e:
        print(f"Error al registrar debug: {str(e)}")
