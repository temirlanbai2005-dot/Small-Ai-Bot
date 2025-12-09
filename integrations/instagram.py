"""
Instagram/Threads - временно отключены
Будут добавлены позже после стабилизации бота
"""

import logging

logger = logging.getLogger(__name__)

def is_instagram_configured():
    """Instagram пока отключен"""
    return False

async def post_to_instagram(caption: str, image_path: str) -> dict:
    """Публикация в Instagram - временно отключена"""
    logger.info("ℹ️ Instagram интеграция будет добавлена позже")
    return {
        'success': False, 
        'error': 'Instagram integration coming soon'
    }

async def post_to_threads(text: str) -> dict:
    """Публикация в Threads - временно отключена"""
    logger.info("ℹ️ Threads интеграция будет добавлена позже")
    return {
        'success': False, 
        'error': 'Threads integration coming soon'
    }
