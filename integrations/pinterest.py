"""
Интеграция с Pinterest API
"""

import logging
import aiohttp
from config.settings import PINTEREST_ACCESS_TOKEN

logger = logging.getLogger(__name__)

PINTEREST_API_URL = "https://api.pinterest.com/v5"

async def post_to_pinterest(title: str, description: str, image_url: str, link: str = None, board_id: str = None) -> dict:
    """
    Создание пина в Pinterest
    
    Args:
        title: Заголовок пина
        description: Описание
        image_url: URL изображения
        link: Ссылка (опционально)
        board_id: ID доски (обязательно)
    
    Returns:
        dict: {'success': bool, 'url': str, 'pin_id': str}
    """
    if not PINTEREST_ACCESS_TOKEN:
        logger.error("Pinterest Access Token не настроен")
        return {'success': False, 'error': 'Token not configured'}
    
    if not board_id:
        logger.error("Board ID обязателен для Pinterest")
        return {'success': False, 'error': 'Board ID required'}
    
    try:
        headers = {
            'Authorization': f'Bearer {PINTEREST_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'board_id': board_id,
            'title': title,
            'description': description,
            'media_source': {
                'source_type': 'image_url',
                'url': image_url
            }
        }
        
        if link:
            data['link'] = link
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{PINTEREST_API_URL}/pins",
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                
                if response.status != 201:
                    error_text = await response.text()
                    logger.error(f"Pinterest API error: {error_text}")
                    return {'success': False, 'error': error_text}
                
                result = await response.json()
                pin_id = result.get('id')
                pin_url = result.get('link') or f"https://www.pinterest.com/pin/{pin_id}/"
                
                logger.info(f"✅ Пин создан в Pinterest: {pin_url}")
                
                return {
                    'success': True,
                    'url': pin_url,
                    'pin_id': pin_id
                }
    
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка HTTP при публикации в Pinterest: {e}")
        return {'success': False, 'error': str(e)}
    
    except Exception as e:
        logger.error(f"Неожиданная ошибка Pinterest: {e}")
        return {'success': False, 'error': str(e)}

async def get_pinterest_boards() -> list:
    """Получение списка досок пользователя"""
    try:
        headers = {
            'Authorization': f'Bearer {PINTEREST_ACCESS_TOKEN}'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{PINTEREST_API_URL}/boards",
                headers=headers,
                timeout=15
            ) as response:
                
                if response.status != 200:
                    return []
                
                result = await response.json()
                boards = []
                
                for board in result.get('items', []):
                    boards.append({
                        'id': board['id'],
                        'name': board['name'],
                        'description': board.get('description', ''),
                        'pin_count': board.get('pin_count', 0)
                    })
                
                return boards
    
    except Exception as e:
        logger.error(f"Ошибка получения досок Pinterest: {e}")
        return []

async def delete_pinterest_pin(pin_id: str) -> bool:
    """Удаление пина"""
    try:
        headers = {
            'Authorization': f'Bearer {PINTEREST_ACCESS_TOKEN}'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{PINTEREST_API_URL}/pins/{pin_id}",
                headers=headers,
                timeout=15
            ) as response:
                
                if response.status == 204:
                    logger.info(f"✅ Пин {pin_id} удален")
                    return True
                
                return False
    
    except Exception as e:
        logger.error(f"Ошибка удаления пина: {e}")
        return False
