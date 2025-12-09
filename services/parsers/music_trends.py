"""
Парсер музыкальных трендов (TikTok, Billboard)
"""

import logging
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from database.db import get_db_pool
import json

logger = logging.getLogger(__name__)

BILLBOARD_HOT_100_URL = "https://www.billboard.com/charts/hot-100/"
TIKTOK_VIRAL_URL = "https://www.tiktok.com/music/trending"

async def get_music_trends(limit: int = 20, use_cache: bool = True) -> list:
    """
    Получение музыкальных трендов (объединенные данные)
    
    Returns:
        list: [{'title': str, 'artist': str, 'position': int, 'source': str}]
    """
    
    # Проверяем кэш
    if use_cache:
        cached_data = await _get_cached_music()
        if cached_data:
            logger.info("Используем кэшированные музыкальные тренды")
            return cached_data[:limit]
    
    try:
        # Получаем тренды из разных источников
        billboard_trends = await get_billboard_trends(limit=15)
        tiktok_trends = await get_tiktok_trends(limit=10)
        
        # Объединяем (Billboard приоритетнее)
        all_trends = billboard_trends + tiktok_trends
        
        # Удаляем дубликаты
        seen = set()
        unique_trends = []
        for trend in all_trends:
            key = f"{trend['title']}_{trend['artist']}"
            if key not in seen:
                seen.add(key)
                unique_trends.append(trend)
        
        result = unique_trends[:limit]
        
        # Сохраняем в кэш
        if result:
            await _cache_music(result)
        
        logger.info(f"✅ Получено {len(result)} музыкальных трендов")
        return result
    
    except Exception as e:
        logger.error(f"Ошибка получения музыкальных трендов: {e}")
        return await _get_fallback_music(limit)

async def get_billboard_trends(limit: int = 15) -> list:
    """
    Парсинг Billboard Hot 100
    """
    try:
        logger.info("Парсим Billboard Hot 100...")
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with session.get(BILLBOARD_HOT_100_URL, headers=headers, timeout=15) as response:
                if response.status != 200:
                    logger.error(f"Billboard вернул статус {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                trends = []
                
                # Парсинг структуры Billboard
                chart_items = soup.find_all('li', class_='o-chart-results-list__item')
                
                for i, item in enumerate(chart_items[:limit], 1):
                    try:
                        title_elem = item.find('h3', class_='c-title')
                        artist_elem = item.find('span', class_='c-label')
                        
                        if title_elem and artist_elem:
                            title = title_elem.get_text(strip=True)
                            artist = artist_elem.get_text(strip=True)
                            
                            trends.append({
                                'title': title,
                                'artist': artist,
                                'position': i,
                                'source': 'Billboard Hot 100',
                                'url': f'https://www.billboard.com/charts/hot-100/'
                            })
                    except Exception as e:
                        logger.warning(f"Ошибка парсинга элемента Billboard: {e}")
                        continue
                
                logger.info(f"✅ Получено {len(trends)} треков с Billboard")
                return trends
    
    except Exception as e:
        logger.error(f"Ошибка парсинга Billboard: {e}")
        return []

async def get_tiktok_trends(limit: int = 10) -> list:
    """
    Получение трендовой музыки TikTok
    (Упрощенная версия, так как TikTok требует авторизации)
    """
    try:
        logger.info("Получаем тренды TikTok...")
        
        # Используем альтернативный источник - TokBoard
        url = "https://tokboard.com/api/trends/music"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    logger.warning("TikTok API недоступен, используем fallback")
                    return await _get_tiktok_fallback()
                
                data = await response.json()
                
                trends = []
                for i, item in enumerate(data.get('data', [])[:limit], 1):
                    trends.append({
                        'title': item.get('title', 'Unknown'),
                        'artist': item.get('author', 'Unknown Artist'),
                        'position': i,
                        'source': 'TikTok Viral',
                        'plays': item.get('playCount', 0),
                    })
                
                logger.info(f"✅ Получено {len(trends)} треков с TikTok")
                return trends
    
    except Exception as e:
        logger.error(f"Ошибка получения TikTok трендов: {e}")
        return await _get_tiktok_fallback()

async def _get_tiktok_fallback() -> list:
    """
    Fallback данные для TikTok (популярные треки)
    """
    # Можно использовать Spotify Viral Charts или другой источник
    logger.info("Используем fallback для TikTok трендов")
    
    return [
        {'title': 'Check TikTok', 'artist': 'Various Artists', 'position': 1, 'source': 'TikTok'},
    ]

async def _get_cached_music() -> list:
    """Получение музыки из кэша"""
    db_pool = get_db_pool()
    if not db_pool:
        return None
    
    try:
        async with db_pool.acquire() as conn:
            # Кэш действителен 12 часов
            cache_time = datetime.now() - timedelta(hours=12)
            
            cached = await conn.fetchrow('''
                SELECT data 
                FROM trends_cache 
                WHERE trend_type = 'music' 
                AND cached_at > $1
                ORDER BY cached_at DESC 
                LIMIT 1
            ''', cache_time)
            
            if cached:
                return cached['data']
    
    except Exception as e:
        logger.error(f"Ошибка чтения кэша музыки: {e}")
    
    return None

async def _cache_music(trends: list):
    """Сохранение музыки в кэш"""
    db_pool = get_db_pool()
    if not db_pool:
        return
    
    try:
        async with db_pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO trends_cache (trend_type, data)
                VALUES ('music', $1)
            ''', trends)
            
            logger.info("✅ Музыкальные тренды сохранены в кэш")
    
    except Exception as e:
        logger.error(f"Ошибка сохранения кэша музыки: {e}")

async def _get_fallback_music(limit: int) -> list:
    """Fallback данные для музыки"""
    logger.warning("Используем fallback данные для музыки")
    
    # Пытаемся получить старый кэш
    db_pool = get_db_pool()
    if db_pool:
        try:
            async with db_pool.acquire() as conn:
                cached = await conn.fetchrow('''
                    SELECT data 
                    FROM trends_cache 
                    WHERE trend_type = 'music'
                    ORDER BY cached_at DESC 
                    LIMIT 1
                ''')
                
                if cached:
                    return cached['data'][:limit]
        except:
            pass
    
    # Заглушка
    return [{
        'title': 'Music Trends',
        'artist': 'Check Billboard & TikTok',
        'position': 1,
        'source': 'Fallback',
    }]

async def search_track_on_spotify(track_name: str, artist: str) -> dict:
    """
    Поиск трека в Spotify (опционально, требует API ключ)
    """
    # Заглушка для будущей реализации
    return {
        'spotify_url': f'https://open.spotify.com/search/{track_name}',
        'preview_url': None,
    }
