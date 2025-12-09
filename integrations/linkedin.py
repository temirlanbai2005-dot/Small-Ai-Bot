"""
Интеграция с LinkedIn API
"""

import logging
import aiohttp
from config.settings import LINKEDIN_ACCESS_TOKEN

logger = logging.getLogger(__name__)

LINKEDIN_API_URL = "https://api.linkedin.com/v2"

async def post_to_linkedin(text: str, image_url: str = None) -> dict:
    """
    Публикация поста в LinkedIn
    
    Args:
        text: Текст поста (до 3000 символов)
        image_url: URL изображения (опционально)
    
    Returns:
        dict: {'success': bool, 'url': str, 'post_id': str}
    """
    if not LINKEDIN_ACCESS_TOKEN:
        logger.error("LinkedIn Access Token не настроен")
        return {'success': False, 'error': 'Token not configured'}
    
    try:
        headers = {
            'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        # Получаем ID пользователя
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{LINKEDIN_API_URL}/me",
                headers=headers,
                timeout=15
            ) as response:
                
                if response.status != 200:
                    error = await response.text()
                    logger.error(f"Ошибка получения профиля LinkedIn: {error}")
                    return {'success': False, 'error': error}
                
                user_data = await response.json()
                user_id = user_data['id']
        
        # Обрезаем текст если нужно
        if len(text) > 3000:
            text = text[:2997] + '...'
        
        # Создаем пост
        post_data = {
            'author': f'urn:li:person:{user_id}',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': text
                    },
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }
        
        # Если есть изображение
        if image_url:
            post_data['specificContent']['com.linkedin.ugc.ShareContent']['shareMediaCategory'] = 'IMAGE'
            post_data['specificContent']['com.linkedin.ugc.ShareContent']['media'] = [{
                'status': 'READY',
                'media': image_url,
                'title': {
                    'text': 'Image'
                }
            }]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{LINKEDIN_API_URL}/ugcPosts",
                headers=headers,
                json=post_data,
                timeout=30
            ) as response:
                
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    logger.error(f"LinkedIn API error: {error_text}")
                    return {'success': False, 'error': error_text}
                
                result = await response.json()
                post_id = result.get('id', '').split(':')[-1]
                
                # LinkedIn не возвращает прямую ссылку, формируем сами
                post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
                
                logger.info(f"✅ Пост опубликован в LinkedIn: {post_url}")
                
                return {
                    'success': True,
                    'url': post_url,
                    'post_id': post_id
                }
    
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка HTTP при публикации в LinkedIn: {e}")
        return {'success': False, 'error': str(e)}
    
    except Exception as e:
        logger.error(f"Неожиданная ошибка LinkedIn: {e}")
        return {'success': False, 'error': str(e)}

async def get_linkedin_profile() -> dict:
    """Получение информации о профиле"""
    try:
        headers = {
            'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{LINKEDIN_API_URL}/me",
                headers=headers,
                timeout=15
            ) as response:
                
                if response.status != 200:
                    return {}
                
                data = await response.json()
                return {
                    'id': data.get('id'),
                    'firstName': data.get('localizedFirstName'),
                    'lastName': data.get('localizedLastName'),
                }
    
    except Exception as e:
        logger.error(f"Ошибка получения профиля LinkedIn: {e}")
        return {}

async def delete_linkedin_post(post_id: str) -> bool:
    """Удаление поста из LinkedIn"""
    try:
        headers = {
            'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{LINKEDIN_API_URL}/ugcPosts/{post_id}",
                headers=headers,
                timeout=15
            ) as response:
                
                if response.status == 204:
                    logger.info(f"✅ Пост {post_id} удален из LinkedIn")
                    return True
                
                return False
    
    except Exception as e:
        logger.error(f"Ошибка удаления поста LinkedIn: {e}")
        return False
