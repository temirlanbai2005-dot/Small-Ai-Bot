"""
Настройка логирования
"""

import logging
import sys

def setup_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """Настройка логгера"""
    logger = logging.getLogger(name or __name__)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# Создаем глобальный логгер
logger = setup_logger('TelegramBot')
