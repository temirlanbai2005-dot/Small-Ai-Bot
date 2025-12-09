"""
Парсер трендов с ArtStation
"""

import logging
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from database.db import get_db_pool

logger = logging.getLogger(__name__)

ARTSTATION_URL = "https://www.artstation.com/artwork"
ARTSTATION_API = "https://www.artstation.com/api/v2/community/explore/projects/trending.json"

async def get_artstation_trends(limit: int = 10, use_cache: bool = True) -> list:
    """
    Получение трендовых 3D-артов с ArtStation
    
    Returns:
        list: [{'title': str, 'artist': str, 'url': str, 'likes': int, 'views': int, 'thumbnail': str}]
    """
    
    # Проверяем кэш
    if use_cache:
        cached_data = await _get_cached_trends()
        if cached_data:
            logger.info("Используем кэшированные тренды ArtStation")
            return cached_data[:limit]
    
    try:
        logger.info("Парсим свежие тренды с ArtStation...")
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Используем официальное API ArtStation
            async with session.get(ARTSTATION_API, headers=headers, timeout=15) as response:
                if response.status != 200:
                    logger.error(f"ArtStation API вернул статус {response.status}")
                    return await _get_fallback_trends(limit)
                
                data = await response.json()
                
                trends = []
                for item in data.get('data', [])[:limit]:
                    trend = {
                        'title': item.get('title', 'Untitled'),
                        'artist': item.get('user', {}).get('full_name', 'Unknown Artist'),
                        'username': item.get('user', {}).get('username', ''),
                        'url': item.get('permalink', ''),
                        'likes': item.get('likes_count', 0),
                        'views': item.get('views_count', 0),
                        'thumbnail': item.get('cover', {}).get('thumb_url', ''),
                        'medium': item.get('medium', {}).get('name', '3D'),
                        'tags': [tag.get('name') for tag in item.get('tags', [])[:5]],
                    }
                    trends.append(trend)
                
                # Сохраняем в кэш
                if trends:
                    await _cache_trends(trends)
                
                logger.info(f"✅ Получено {len(trends)} трендов с ArtStation")
                return trends
    
    except asyncio.TimeoutError:
        logger.error("Таймаут при парсинге ArtStation")
        return await _get_fallback_trends(limit)
    
    except Exception as e:
        logger.error(f"Ошибка парсинга ArtStation: {e}")
        return await _get_fallback_trends(limit)

async def _get_cached_trends() -> list:
    """Получение трендов из кэша"""
    db_pool = get_db_pool()
    if not db_pool:
        return None
    
    try:
        async with db_pool.acquire() as conn:
            # Кэш действителен 6 часов
            cache_time = datetime.now() - timedelta(hours=6)
            
            cached = await conn.fetchrow('''
                SELECT data, cached_at 
                FROM trends_cache 
                WHERE trend_type = 'artstation' 
                AND cached_at > $1
                ORDER BY cached_at DESC 
                LIMIT 1
            ''', cache_time)
            
            if cached:
                logger.info(f"Кэш найден: {cached['cached_at']}")
                return cached['data']
    
    except Exception as e:
        logger.error(f"Ошибка чтения кэша: {e}")
    
    return None

async def _cache_trends(trends: list):
    """Сохранение трендов в кэш"""
    db_pool = get_db_pool()
    if not db_pool:
        return
    
    try:
        async with db_pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO trends_cache (trend_type, data)
                VALUES ('artstation', $1)
            ''', trends)
            
            logger.info("✅ Тренды сохранены в кэш")
    
    except Exception as e:
        logger.error(f"Ошибка сохранения кэша: {e}")

async def _get_fallback_trends(limit: int) -> list:
    """Fallback данные если парсинг не удался"""
    logger.warning("Используем fallback данные")
    
    # Пытаемся получить старый кэш (даже устаревший)
    db_pool = get_db_pool()
    if db_pool:
        try:
            async with db_pool.acquire() as conn:
                cached = await conn.fetchrow('''
                    SELECT data 
                    FROM trends_cache 
                    WHERE trend_type = 'artstation'
                    ORDER BY cached_at DESC 
                    LIMIT 1
                ''')
                
                if cached:
                    return cached['data'][:limit]
        except:
            pass
    
    # Возвращаем заглушку
    return [{
        'title': 'ArtStation Trending',
        'artist': 'Top Artists',
        'url': 'https://www.artstation.com/trending',
        'likes': 0,
        'views': 0,
        'thumbnail': '',
        'medium': '3D',
        'tags': [],
    }]

async def get_artstation_user_works(username: str, limit: int = 5) -> list:
    """
    Получение работ конкретного артиста
    """
    try:
        url = f"https://www.artstation.com/users/{username}/projects.json"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                
                works = []
                for item in data.get('data', [])[:limit]:
                    work = {
                        'title': item.get('title', 'Untitled'),
                        'url': item.get('permalink', ''),
                        'thumbnail': item.get('cover', {}).get('thumb_url', ''),
                        'likes': item.get('likes_count', 0),
                    }
                    works.append(work)
                
                return works
    
    except Exception as e:
        logger.error(f"Ошибка получения работ артиста: {e}")
        return []
