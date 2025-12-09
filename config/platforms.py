"""
Конфигурация платформ для публикации контента
Оптимальное время постинга на основе данных 2025 года
"""

# ========================================
# ЛУЧШЕЕ ВРЕМЯ ПОСТИНГА (UTC+3 Moscow)
# ========================================

BEST_POSTING_TIMES = {
    'Instagram': {
        'weekdays': [9, 11, 13, 15, 19, 21],  # Пн-Пт
        'weekend': [10, 12, 14, 18, 20],      # Сб-Вс
        'best': [11, 13, 19],                 # Топ-3 времени
        'description': 'Лучшее время: 11:00, 13:00, 19:00 (будни)',
    },
    'TikTok': {
        'weekdays': [7, 9, 12, 16, 19, 21],
        'weekend': [9, 11, 16, 20],
        'best': [9, 12, 19],
        'description': 'Лучшее время: 09:00, 12:00, 19:00',
    },
    'X (Twitter)': {
        'weekdays': [8, 9, 12, 13, 17, 18],
        'weekend': [9, 11, 14],
        'best': [9, 12, 17],
        'description': 'Лучшее время: 09:00, 12:00, 17:00',
    },
    'YouTube': {
        'weekdays': [14, 15, 16, 17, 18, 19, 20],
        'weekend': [9, 10, 11, 14, 15, 19],
        'best': [15, 17, 19],
        'description': 'Лучшее время: 15:00-20:00 (вечер)',
    },
    'LinkedIn': {
        'weekdays': [7, 8, 9, 12, 17, 18],
        'weekend': [],  # LinkedIn не активен в выходные
        'best': [8, 12, 17],
        'description': 'Лучшее время: 08:00, 12:00, 17:00 (только будни)',
    },
    'Pinterest': {
        'weekdays': [14, 15, 20, 21],
        'weekend': [15, 20, 21],
        'best': [15, 20, 21],
        'description': 'Лучшее время: 15:00, 20:00-21:00 (вечер)',
    },
    'Threads': {
        'weekdays': [9, 11, 13, 15, 19, 21],
        'weekend': [10, 12, 14, 18, 20],
        'best': [11, 13, 19],
        'description': 'Аналогично Instagram: 11:00, 13:00, 19:00',
    },
    'Telegram': {
        'weekdays': [8, 9, 12, 13, 18, 19, 20, 21],
        'weekend': [10, 12, 18, 20],
        'best': [9, 13, 19],
        'description': 'Лучшее время: 09:00, 13:00, 19:00',
    },
    'ArtStation': {
        'weekdays': [10, 14, 16, 18],
        'weekend': [12, 16, 18],
        'best': [14, 16, 18],
        'description': 'Международная аудитория: 14:00-18:00 (UTC+3)',
    },
}

# ========================================
# ДЕТАЛЬНАЯ КОНФИГУРАЦИЯ ПЛАТФОРМ
# ========================================

PLATFORMS_CONFIG = {
    'Instagram': {
        'name': 'Instagram',
        'emoji': '📷',
        'enabled': True,
        'auto_post': True,
        'max_length': 2200,
        'max_hashtags': 30,
        'supports_images': True,
        'supports_video': True,
        'aspect_ratio': '1:1, 4:5, 9:16',
        'audience': 'Широкая аудитория креаторов',
        'content_type': 'Визуальный контент, процесс работы, тизеры',
    },
    'TikTok': {
        'name': 'TikTok',
        'emoji': '🎵',
        'enabled': True,
        'auto_post': True,
        'max_length': 2200,
        'max_hashtags': 20,
        'supports_images': False,
        'supports_video': True,
        'aspect_ratio': '9:16',
        'audience': 'Молодая аудитория 18-30 лет',
        'content_type': 'Короткие видео, процессы, таймлапсы',
    },
    'X (Twitter)': {
        'name': 'X (Twitter)',
        'emoji': '🐦',
        'enabled': True,
        'auto_post': True,
        'max_length': 280,
        'max_hashtags': 5,
        'supports_images': True,
        'supports_video': True,
        'aspect_ratio': '16:9',
        'audience': 'Профессионалы и энтузиасты',
        'content_type': 'Короткие апдейты, WIP, анонсы',
    },
    'YouTube': {
        'name': 'YouTube',
        'emoji': '▶️',
        'enabled': True,
        'auto_post': True,
        'max_length': 5000,
        'max_hashtags': 15,
        'supports_images': False,
        'supports_video': True,
        'aspect_ratio': '16:9',
        'audience': 'Международная аудитория',
        'content_type': 'Длинные туториалы, брейкдауны, таймлапсы',
    },
    'LinkedIn': {
        'name': 'LinkedIn',
        'emoji': '💼',
        'enabled': True,
        'auto_post': True,
        'max_length': 3000,
        'max_hashtags': 10,
        'supports_images': True,
        'supports_video': True,
        'aspect_ratio': '1:1, 16:9',
        'audience': 'Профессионалы, студии, рекрутеры',
        'content_type': 'Кейс-стади, достижения, профессиональный контент',
    },
    'Pinterest': {
        'name': 'Pinterest',
        'emoji': '📌',
        'enabled': True,
        'auto_post': True,
        'max_length': 500,
        'max_hashtags': 20,
        'supports_images': True,
        'supports_video': True,
        'aspect_ratio': '2:3',
        'audience': 'Креативщики, дизайнеры',
        'content_type': 'Вертикальные изображения, вдохновение, туториалы',
    },
    'Threads': {
        'name': 'Threads',
        'emoji': '🧵',
        'enabled': True,
        'auto_post': True,
        'max_length': 500,
        'max_hashtags': 10,
        'supports_images': True,
        'supports_video': True,
        'aspect_ratio': '1:1, 4:5',
        'audience': 'Аудитория Instagram/Meta',
        'content_type': 'Короткие посты, обсуждения, мысли',
    },
    'Telegram': {
        'name': 'Telegram',
        'emoji': '✈️',
        'enabled': True,
        'auto_post': True,
        'max_length': 4096,
        'max_hashtags': 99,
        'supports_images': True,
        'supports_video': True,
        'aspect_ratio': 'Любой',
        'audience': 'Подписчики канала',
        'content_type': 'Любой контент, анонсы, апдейты',
    },
    'ArtStation': {
        'name': 'ArtStation',
        'emoji': '🎨',
        'enabled': False,  # Требует ручной публикации
        'auto_post': False,
        'max_length': 1000,
        'max_hashtags': 50,
        'supports_images': True,
        'supports_video': True,
        'aspect_ratio': 'Любой (рекомендуется 16:9)',
        'audience': 'Профессиональные 3D/2D артисты',
        'content_type': 'Финальные работы, портфолио',
    },
}

# ========================================
# ХЭШТЕГИ ДЛЯ РАЗНЫХ ТИПОВ КОНТЕНТА
# ========================================

HASHTAG_TEMPLATES = {
    '3d_art': [
        '#3dart', '#3dartist', '#3dmodeling', '#cgi', '#digitalart',
        '#3drender', '#blender', '#cinema4d', '#maya', '#zbrush',
        '#substancepainter', '#render', '#3ddesign', '#cgiart', '#3danimation'
    ],
    'gamedev': [
        '#gamedev', '#indiegame', '#gamedevelopment', '#gameart', '#gamedesign',
        '#unrealengine', '#unity3d', '#indiedev', '#gaming', '#videogames'
    ],
    'vfx': [
        '#vfx', '#visualeffects', '#motiongraphics', '#motiondesign', '#aftereffects',
        '#houdini', '#nuke', '#filmmaking', '#postproduction', '#cgi'
    ],
    'animation': [
        '#animation', '#3danimation', '#motiongraphics', '#animationart', '#animator',
        '#characteranimation', '#motiondesign', '#animate', '#animated', '#motion'
    ],
    'design': [
        '#design', '#designer', '#digitaldesign', '#creative', '#art',
        '#graphicdesign', '#productdesign', '#visualization', '#rendering', '#artwork'
    ],
}

# ========================================
# ЭМОДЗИ ДЛЯ КОНТЕНТА
# ========================================

CONTENT_EMOJIS = {
    'wip': '🚧',           # Work in Progress
    'finished': '✨',      # Готовая работа
    'tutorial': '📚',     # Туториал
    'timelapse': '⏱️',    # Таймлапс
    'breakdown': '🔍',    # Брейкдаун
    'announcement': '📢', # Анонс
    'question': '❓',     # Вопрос
    'tip': '💡',          # Совет
    'resource': '🎁',     # Ресурс
    'collaboration': '🤝', # Коллаборация
}

def get_platform_config(platform_name: str) -> dict:
    """Получить конфигурацию платформы"""
    return PLATFORMS_CONFIG.get(platform_name, {})

def get_best_times(platform_name: str, is_weekend: bool = False) -> list:
    """Получить лучшее время для публикации"""
    platform = BEST_POSTING_TIMES.get(platform_name, {})
    if is_weekend:
        return platform.get('weekend', platform.get('weekdays', []))
    return platform.get('weekdays', [])

def get_recommended_hashtags(content_type: str, limit: int = 10) -> list:
    """Получить рекомендуемые хэштеги"""
    hashtags = HASHTAG_TEMPLATES.get(content_type, HASHTAG_TEMPLATES['3d_art'])
    return hashtags[:limit]
