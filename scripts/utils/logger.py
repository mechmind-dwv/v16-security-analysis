"""
Configuración centralizada de logging
"""
import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logger(name: str, log_file: str = None, level: str = "INFO"):
    """Configura un logger con formato consistente"""
    
    logger = logging.getLogger(name)
    
    if logger.hasHandlers():
        logger.handlers.clear()
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo si se especifica
    if log_file:
        # Crear directorio si no existe
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_timestamp() -> str:
    """Retorna timestamp formateado"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
