"""
Интеграция с TikTok API
"""

import logging
import aiohttp
from config.settings import TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_ACCESS_TOKEN

logger = logging.getLogger(__name__)

TIKTOK_API_URL = "https://open.tiktokapis.com/v2"

async def post_to_tiktok(video_path: str, caption: str, hashtags: list = None) -> dict:
    """
    Загрузка видео в TikTok
    
    Note: TikTok API требует одобрения и работает только с бизнес-аккаунтами
    
    Args:
        video_path: Путь к видео файлу
        caption: Описание видео
        hashtags: Список хештегов
    
    Returns:
        dict: {'success': bool, 'url': str, 'video_id': str}
    """
    if not TIKTOK_CLIENT_KEY or not TIKTOK_ACCESS_TOKEN:
        logger.error("TikTok API не настроен")
        return {'success': False, 'error': 'API not configured'}
    
    try:
        headers = {
            'Authorization': f'Bearer {TIKTOK_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Формируем описание с хештегами
        full_caption = caption
        if hashtags:
            full_caption += ' ' + ' '.join(hashtags)
        
        # Обрезаем если слишком длинный
        if len(full_caption) > 2200:
            full_caption = full_caption[:2197] + '...'
        
        # TikTok требует сначала инициализировать загрузку
        init_data = {
            'post_info': {
                'title': full_caption,
                'privacy_level': 'PUBLIC_TO_EVERYONE',
                'disable_duet': False,
                'disable_comment': False,
                'disable_stitch': False,
                'video_cover_timestamp_ms': 1000
            },
            'source_info': {
                'source': 'FILE_UPLOAD',
                'video_size': os.path.getsize(video_path),
                'chunk_size': 10000000,
                'total_chunk_count': 1
            }
        }
        
        async with aiohttp.ClientSession() as session:
            # Инициализация загрузки
            async with session.post(
                f"{TIKTOK_API_URL}/post/publish/inbox/video/init/",
                headers=headers,
                json=init_data,
                timeout=30
            ) as response:
                
                if response.status != 200:
                    error = await response.text()
                    logger.error(f"TikTok init error: {error}")
                    return {'success': False, 'error': error}
                
                init_result = await response.json()
                publish_id = init_result['data']['publish_id']
                upload_url = init_result['data']['upload_url']
            
            # Загрузка видео
            with open(video_path, 'rb') as video_file:
                async with session.put(
                    upload_url,
                    data=video_file,
                    timeout=300
                ) as upload_response:
                    
                    if upload_response.status != 200:
                        return {'success': False, 'error': 'Upload failed'}
            
            # Публикация
            async with session.post(
                f"{TIKTOK_API_URL}/post/publish/status/fetch/",
                headers=headers,
                json={'publish_id': publish_id},
                timeout=30
            ) as status_response:
                
                result = await status_response.json()
                
                if result.get('data', {}).get('status') == 'PUBLISH_COMPLETE':
                    video_id = result['data']['video_id']
                    video_url = f"https://www.tiktok.com/@{INSTAGRAM_USERNAME}/video/{video_id}"
                    
                    logger.info(f"✅ Видео опубликовано в TikTok: {video_url}")
                    
                    return {
                        'success': True,
                        'url': video_url,
                        'video_id': video_id
                    }
                else:
                    return {'success': False, 'error': 'Publishing failed'}
    
    except Exception as e:
        logger.error(f"Ошибка публикации в TikTok: {e}")
        return {'success': False, 'error': str(e)}

async def get_tiktok_user_info() -> dict:
    """Получение информации о пользователе TikTok"""
    try:
        if not TIKTOK_ACCESS_TOKEN:
            return {}
        
        headers = {
            'Authorization': f'Bearer {TIKTOK_ACCESS_TOKEN}'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{TIKTOK_API_URL}/user/info/",
                headers=headers,
                timeout=15
            ) as response:
                
                if response.status != 200:
                    return {}
                
                data = await response.json()
                user = data.get('data', {}).get('user', {})
                
                return {
                    'display_name': user.get('display_name'),
                    'follower_count': user.get('follower_count', 0),
                    'following_count': user.get('following_count', 0),
                    'likes_count': user.get('likes_count', 0),
                    'video_count': user.get('video_count', 0),
                }
    
    except Exception as e:
        logger.error(f"Ошибка получения информации TikTok: {e}")
        return {}
