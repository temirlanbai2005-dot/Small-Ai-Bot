"""
Настройка логирования
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Настройка логгера с красивым форматированием
    """
    logger = logging.getLogger(name or __name__)
    logger.setLevel(level)
    
    # Избегаем дублирования handlers
    if logger.handlers:
        return logger
    
    # Формат логов
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Консольный handler с цветами
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(console_handler)
    
    # Файловый handler (опционально)
    try:
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'bot_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Не удалось создать файловый логгер: {e}")
    
    return logger

class ColoredFormatter(logging.Formatter):
    """
    Цветной форматтер для консоли
    """
    
    # ANSI цвета
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

# Создаем глобальный логгер
logger = setup_logger('TelegramBot')
