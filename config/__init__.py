"""
Модуль конфигурации бота
"""

from .settings import *
from .platforms import (
    PLATFORMS_CONFIG, 
    BEST_POSTING_TIMES, 
    SUPPORTED_PLATFORMS,
    HASHTAG_TEMPLATES,
    CONTENT_EMOJIS,
    get_platform_config,
    get_best_times,
    get_recommended_hashtags
)

__all__ = [
    'TELEGRAM_TOKEN',
    'GEMINI_API_KEY',
    'DATABASE_URL',
    'PORT',
    'PLATFORMS_CONFIG',
    'BEST_POSTING_TIMES',
    'SUPPORTED_PLATFORMS',
    'HASHTAG_TEMPLATES',
    'CONTENT_EMOJIS',
    'get_platform_config',
    'get_best_times',
    'get_recommended_hashtags',
]
