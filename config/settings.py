"""
Настройки и конфигурация бота
"""

import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# ========================================
# ОСНОВНЫЕ НАСТРОЙКИ
# ========================================

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
PORT = int(os.getenv('PORT', 10000))

# Telegram канал для автопостинга
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', '')

# Часовой пояс
TIMEZONE = os.getenv('TZ', 'Europe/Moscow')

# ========================================
# СОЦИАЛЬНЫЕ СЕТИ - API КЛЮЧИ
# ========================================

# Twitter/X
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET', '')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')

# YouTube
YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID', '')
YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET', '')
YOUTUBE_REFRESH_TOKEN = os.getenv('YOUTUBE_REFRESH_TOKEN', '')

# LinkedIn
LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID', '')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET', '')
LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN', '')

# Pinterest
PINTEREST_ACCESS_TOKEN = os.getenv('PINTEREST_ACCESS_TOKEN', '')

# Instagram/Threads
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', '')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD', '')

# TikTok
TIKTOK_CLIENT_KEY = os.getenv('TIKTOK_CLIENT_KEY', '')
TIKTOK_CLIENT_SECRET = os.getenv('TIKTOK_CLIENT_SECRET', '')
TIKTOK_ACCESS_TOKEN = os.getenv('TIKTOK_ACCESS_TOKEN', '')

# ========================================
# НАСТРОЙКИ ПАРСИНГА
# ========================================

USE_SELENIUM = os.getenv('USE_SELENIUM', 'false').lower() == 'true'
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', '/usr/bin/chromedriver')

# User-Agent для парсинга
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# ========================================
# НАСТРОЙКИ УВЕДОМЛЕНИЙ
# ========================================

# Время автоматических уведомлений (часы в формате 24ч)
NOTIFICATION_TIMES = {
    'motivation': 8,      # 08:00 - Мотивация дня
    'idea': 9,           # 09:00 - Идея дня
    'trends': 10,        # 10:00 - Тренды
    'jobs': 11,          # 11:00 - Вакансии
    'assets': 12,        # 12:00 - Топ ассетов
}

# Интервал напоминаний "пей воду" (в часах)
REMINDER_INTERVAL_HOURS = 2

# ========================================
# КОНСТАНТЫ
# ========================================

# Максимальная длина поста для разных платформ (символы)
MAX_POST_LENGTH = {
    'twitter': 280,
    'instagram': 2200,
    'tiktok': 2200,
    'linkedin': 3000,
    'telegram': 4096,
    'youtube': 5000,
    'pinterest': 500,
    'threads': 500,
    'artstation': 1000,
}

# Поддерживаемые платформы
SUPPORTED_PLATFORMS = [
    'Instagram',
    'TikTok',
    'X (Twitter)',
    'YouTube',
    'ArtStation',
    'LinkedIn',
    'Pinterest',
    'Threads',
    'Telegram',
]

# ========================================
# ВАЛИДАЦИЯ
# ========================================

def validate_config():
    """Проверка обязательных переменных окружения"""
    required = {
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'GEMINI_API_KEY': GEMINI_API_KEY,
        'DATABASE_URL': DATABASE_URL,
    }
    
    missing = [key for key, value in required.items() if not value]
    
    if missing:
        raise ValueError(f"❌ Отсутствуют обязательные переменные окружения: {', '.join(missing)}")
    
    return True

# Проверка при импорте
validate_config()
