"""
Модуль конфигурации бота
"""

from .settings import *
from .platforms import PLATFORMS_CONFIG, BEST_POSTING_TIMES

__all__ = [
    'TELEGRAM_TOKEN',
    'GEMINI_API_KEY',
    'DATABASE_URL',
    'PORT',
    'PLATFORMS_CONFIG',
    'BEST_POSTING_TIMES'
]
