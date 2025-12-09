"""
Интеграция с Instagram и Threads
"""

import os
import logging

logger = logging.getLogger(__name__)

INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', '')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD', '')

# Глобальный клиент
_client = None

def is_instagram_configured():
    """Проверка настроен ли Instagram"""
    return bool(INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD)

def get_instagram_client():
    """Получение клиента Instagram"""
    global _client
    
    if not is_instagram_configured():
        logger.warning("⚠️ Instagram не настроен")
        return None
    
    if _client:
        return _client
    
    try:
        from instagrapi import Client
        
        client = Client()
        
        # Пробуем загрузить сессию
        session_file = '/tmp/instagram_session.json'
        
        try:
            if os.path.exists(session_file):
                client.load_settings(session_file)
                client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            else:
                client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                client.dump_settings(session_file)
        except:
            client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            client.dump_settings(session_file)
        
        _client = client
        logger.info("✅ Instagram авторизован")
        return client
    
    except Exception as e:
        logger.error(f"❌ Ошибка авторизации Instagram: {e}")
        return None

async def post_to_instagram(caption: str, image_path: str) -> dict:
    """Публикация фото в Instagram"""
    
    if not is_instagram_configured():
        return {'success': False, 'error': 'Instagram not configured'}
    
    try:
        client = get_instagram_client()
        if not client:
            return {'success': False, 'error': 'Failed to login'}
        
        # Обрезаем если слишком длинный
        if len(caption) > 2200:
            caption = caption[:2197] + '...'
        
        # Публикуем
        media = client.photo_upload(path=image_path, caption=caption)
        
        post_url = f"https://www.instagram.com/p/{media.code}/"
        
        logger.info(f"✅ Пост в Instagram: {post_url}")
        return {'success': True, 'url': post_url, 'media_id': str(media.pk)}
    
    except Exception as e:
        logger.error(f"❌ Ошибка Instagram: {e}")
        return {'success': False, 'error': str(e)}

async def post_to_threads(text: str) -> dict:
    """Публикация в Threads"""
    
    # Threads пока не имеет публичного API
    # Можно использовать через instagrapi в будущем
    
    logger.warning("⚠️ Threads API пока недоступен официально")
    return {'success': False, 'error': 'Threads API not available yet'}
