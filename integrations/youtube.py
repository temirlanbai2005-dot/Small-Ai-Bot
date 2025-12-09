"""
Интеграция с YouTube Data API v3
"""

import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from config.settings import (
    YOUTUBE_CLIENT_ID,
    YOUTUBE_CLIENT_SECRET,
    YOUTUBE_REFRESH_TOKEN
)

logger = logging.getLogger(__name__)

def get_youtube_service():
    """Создание YouTube API сервиса"""
    try:
        if not YOUTUBE_CLIENT_ID or not YOUTUBE_REFRESH_TOKEN:
            logger.error("YouTube API не настроен")
            return None
        
        credentials = Credentials(
            token=None,
            refresh_token=YOUTUBE_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=YOUTUBE_CLIENT_ID,
            client_secret=YOUTUBE_CLIENT_SECRET
        )
        
        service = build('youtube', 'v3', credentials=credentials)
        return service
    
    except Exception as e:
        logger.error(f"Ошибка создания YouTube сервиса: {e}")
        return None

async def post_to_youtube_community(text: str, image_path: str = None) -> dict:
    """
    Публикация в YouTube Community Tab
    
    Note: YouTube Community Posts API доступен только для каналов с 500+ подписчиками
    
    Args:
        text: Текст поста
        image_path: Путь к изображению (опционально)
    
    Returns:
        dict: {'success': bool, 'url': str, 'post_id': str}
    """
    if not YOUTUBE_CLIENT_ID:
        logger.error("YouTube API не настроен")
        return {'success': False, 'error': 'API not configured'}
    
    try:
        service = get_youtube_service()
        if not service:
            return {'success': False, 'error': 'Failed to create service'}
        
        # YouTube Community Posts API
        # ВАЖНО: Эта функция требует специального доступа
        
        # Пока YouTube не предоставляет публичный API для Community Posts
        # Можно использовать только для комментариев к видео
        
        logger.warning("YouTube Community Posts API ограничен")
        
        return {
            'success': False,
            'error': 'YouTube Community API requires special access'
        }
    
    except HttpError as e:
        logger.error(f"Ошибка YouTube API: {e}")
        return {'success': False, 'error': str(e)}
    
    except Exception as e:
        logger.error(f"Неожиданная ошибка YouTube: {e}")
        return {'success': False, 'error': str(e)}

async def upload_youtube_video(title: str, description: str, video_path: str, tags: list = None) -> dict:
    """
    Загрузка видео на YouTube
    
    Args:
        title: Название видео
        description: Описание
        video_path: Путь к видео файлу
        tags: Список тегов
    
    Returns:
        dict: {'success': bool, 'url': str, 'video_id': str}
    """
    try:
        service = get_youtube_service()
        if not service:
            return {'success': False, 'error': 'Service not available'}
        
        from googleapiclient.http import MediaFileUpload
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': '22'  # People & Blogs
            },
            'status': {
                'privacyStatus': 'public'  # или 'private', 'unlisted'
            }
        }
        
        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True,
            mimetype='video/*'
        )
        
        request = service.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = request.execute()
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        logger.info(f"✅ Видео загружено на YouTube: {video_url}")
        
        return {
            'success': True,
            'url': video_url,
            'video_id': video_id
        }
    
    except HttpError as e:
        logger.error(f"Ошибка загрузки видео: {e}")
        return {'success': False, 'error': str(e)}
    
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        return {'success': False, 'error': str(e)}

async def get_channel_info() -> dict:
    """Получение информации о канале"""
    try:
        service = get_youtube_service()
        if not service:
            return {}
        
        request = service.channels().list(
            part='snippet,statistics',
            mine=True
        )
        
        response = request.execute()
        
        if response['items']:
            channel = response['items'][0]
            return {
                'title': channel['snippet']['title'],
                'subscribers': channel['statistics']['subscriberCount'],
                'views': channel['statistics']['viewCount'],
                'videos': channel['statistics']['videoCount'],
            }
        
        return {}
    
    except Exception as e:
        logger.error(f"Ошибка получения информации о канале: {e}")
        return {}
