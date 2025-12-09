"""
Планировщик автоматического парсинга и обновления трендов
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application

from config.settings import TIMEZONE
from services.parsers.artstation import get_artstation_trends
from services.parsers.music_trends import get_music_trends

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone=TIMEZONE)

async def update_artstation_trends():
    """Обновление трендов ArtStation"""
    logger.info("🔄 Обновление трендов ArtStation...")
    
    try:
        trends = await get_artstation_trends(limit=20, use_cache=False)
        logger.info(f"✅ Обновлено {len(trends)} трендов ArtStation")
    except Exception as e:
        logger.error(f"❌ Ошибка обновления трендов ArtStation: {e}")

async def update_music_trends():
    """Обновление музыкальных трендов"""
    logger.info("🔄 Обновление музыкальных трендов...")
    
    try:
        trends = await get_music_trends(limit=30, use_cache=False)
        logger.info(f"✅ Обновлено {len(trends)} музыкальных трендов")
    except Exception as e:
        logger.error(f"❌ Ошибка обновления музыкальных трендов: {e}")

async def start_trends_scheduler(application: Application):
    """Запуск планировщика обновления трендов"""
    
    # Обновляем ArtStation каждые 6 часов
    scheduler.add_job(
        update_artstation_trends,
        CronTrigger(hour='*/6', timezone=TIMEZONE),
        id='update_artstation'
    )
    
    # Обновляем музыку каждые 12 часов
    scheduler.add_job(
        update_music_trends,
        CronTrigger(hour='*/12', timezone=TIMEZONE),
        id='update_music'
    )
    
    # Запускаем сразу при старте
    scheduler.add_job(update_artstation_trends, id='init_artstation')
    scheduler.add_job(update_music_trends, id='init_music')
    
    scheduler.start()
    logger.info("✅ Планировщик трендов запущен")
