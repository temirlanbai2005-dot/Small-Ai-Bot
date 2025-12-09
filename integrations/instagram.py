"""
Интеграция с Instagram и Threads
Использует неофициальную библиотеку instagrapi
"""

import logging
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
from config.settings import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
import os

logger = logging.getLogger(__name__)

# Глобальный клиент Instagram
_instagram_client = None

def get_instagram_client():
    """Получение авторизованного клиента Instagram"""
    global _instagram_client
    
    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        logger.error("Instagram credentials не настроены")
        return None
    
    if _instagram_client:
        return _instagram_client
    
    try:
        client = Client()
        
        # Загружаем сессию если существует
        session_file = 'instagram_session.json'
        if os.path.exists(session_file):
            try:
                client.load_settings(session_file)
                client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                logger.info("✅ Instagram сессия загружена")
            except:
                logger.warning("Не удалось загрузить сессию, выполняем новый вход")
                client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                client.dump_settings(session_file)
        else:
            # Новый вход
            client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            client.dump_settings(session_file)
            logger.info("✅ Instagram авторизация успешна")
        
        _instagram_client = client
        return client
    
    except LoginRequired:
        logger.error("Instagram требует повторной авторизации")
        return None
    
    except ChallengeRequired:
        logger.error("Instagram требует прохождения challenge (проверки безопасности)")
        return None
    
    except Exception as e:
        logger.error(f"Ошибка авторизации Instagram: {e}")
        return None

async def post_to_instagram(caption: str, image_path: str, hashtags: list = None) -> dict:
    """
    Публикация фото в Instagram
    
    Args:
        caption: Описание поста
        image_path: Путь к изображению
        hashtags: Список хештегов
    
    Returns:
        dict: {'success': bool, 'url': str, 'media_id': str}
    """
    if not INSTAGRAM_USERNAME:
        logger.error("Instagram не настроен")
        return {'success': False, 'error': 'Credentials not configured'}
    
    try:
        client = get_instagram_client()
        if not client:
            return {'success': False, 'error': 'Failed to login'}
        
        # Добавляем хештеги
        full_caption = caption
        if hashtags:
            full_caption += '\n\n' + ' '.join(hashtags)
        
        # Обрезаем если слишком длинный
        if len(full_caption) > 2200:
            full_caption = full_caption[:2197] + '...'
        
        # Публикуем фото
        media = client.photo_upload(
            path=image_path,
            caption=full_caption
        )
        
        media_id = media.pk
        media_code = media.code
        post_url = f"https://www.instagram.com/p/{media_code}/"
        
        logger.info(f"✅ Пост опубликован в Instagram: {post_url}")
        
        return {
            'success': True,
            'url': post_url,
            'media_id': str(media_id)
        }
    
    except Exception as e:
        logger.error(f"Ошибка публикации в Instagram: {e}")
        return {'success': False, 'error': str(e)}

async def post_to_threads(text: str) -> dict:
    """
    Публикация в Threads (от Meta)
    
    Note: Threads использует тот же аккаунт что и Instagram
    
    Args:
        text: Текст поста (до 500 символов)
    
    Returns:
        dict: {'success': bool, 'url': str, 'thread_id': str}
    """
    if not INSTAGRAM_USERNAME:
        logger.error("Instagram/Threads не настроен")
        return {'success': False, 'error': 'Credentials not configured'}
    
    try:
        # Threads пока не имеет публичного API
        # Можно использовать неофициальные методы через instagrapi
        
        logger.warning("Threads API пока недоступен официально")
        
        # Альтернатива - публикация как обычного Instagram поста
        return {
            'success': False,
            'error': 'Threads API not available yet'
        }
    
    except Exception as e:
        logger.error(f"Ошибка публикации в Threads: {e}")
        return {'success': False, 'error': str(e)}

async def delete_instagram_post(media_id: str) -> bool:
    """Удаление поста из Instagram"""
    try:
        client = get_instagram_client()
        if not client:
            return False
        
        client.media_delete(media_id)
        logger.info(f"✅ Пост {media_id} удален из Instagram")
        return True
    
    except Exception as e:
        logger.error(f"Ошибка удаления поста Instagram: {e}")
        return False

async def get_instagram_insights(media_id: str) -> dict:
    """Получение статистики поста"""
    try:
        client = get_instagram_client()
        if not client:
            return {}
        
        media = client.media_info(media_id)
        
        return {
            'likes': media.like_count,
            'comments': media.comment_count,
            'views': media.view_count if hasattr(media, 'view_count') else 0,
        }
    
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return {}
