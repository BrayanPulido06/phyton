"""
Maneja el registro de eventos, errores y advertencias en archivo y consola.
"""

import logging
from datetime import datetime
import os
from pathlib import Path


def configurar_logging():
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

    try:
        logger.info(message)
    except Exception as e:
        print(f"Error al registrar info: {str(e)}")

def log_error(message: str):

    try:
        logger.error(message)
    except Exception as e:
        print(f"Error al registrar error: {str(e)}")

def log_warning(message: str):

    try:
        logger.warning(message)
    except Exception as e:
        print(f"Error al registrar warning: {str(e)}")

def log_debug(message: str):

    try:
        logger.debug(message)
    except Exception as e:
        print(f"Error al registrar debug: {str(e)}")
