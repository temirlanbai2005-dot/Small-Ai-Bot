"""
Планировщик уведомлений
"""

import logging
import pytz
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.db import get_db_pool
from services.gemini_ai import generate_motivation, generate_project_idea

logger = logging.getLogger(__name__)

TIMEZONE = pytz.timezone('Europe/Moscow')

# Глобальный бот (будет установлен при setup)
_bot = None

async def send_motivation():
    """08:00 - Мотивация дня"""
    if not _bot:
        return
    
    logger.info("📨 Отправка мотивации...")
    
    db_pool = get_db_pool()
    if not db_pool:
        return
    
    try:
        async with db_pool.acquire() as conn:
            users = await conn.fetch(
                'SELECT user_id FROM notification_settings WHERE motivation = TRUE'
            )
        
        if not users:
            logger.info("Нет пользователей для мотивации")
            return
        
        motivation = await generate_motivation()
        message = f"🌅 **Доброе утро!**\n\n{motivation}\n\n🚀 Отличного дня!"
        
        sent = 0
        for user in users:
            try:
                await _bot.send_message(
                    chat_id=user['user_id'],
                    text=message,
                    parse_mode='Markdown'
                )
                sent += 1
            except Exception as e:
                logger.warning(f"Не удалось отправить {user['user_id']}: {e}")
        
        logger.info(f"✅ Мотивация: {sent}/{len(users)}")
    
    except Exception as e:
        logger.error(f"Ошибка мотивации: {e}")

async def send_idea():
    """09:00 - Идея дня"""
    if not _bot:
        return
    
    logger.info("📨 Отправка идеи...")
    
    db_pool = get_db_pool()
    if not db_pool:
        return
    
    try:
        async with db_pool.acquire() as conn:
            users = await conn.fetch(
                'SELECT user_id FROM notification_settings WHERE idea = TRUE'
            )
        
        if not users:
            return
        
        idea = await generate_project_idea()
        message = f"💡 **Идея дня:**\n\n{idea}\n\n🎨 Начни создавать!"
        
        sent = 0
        for user in users:
            try:
                await _bot.send_message(
                    chat_id=user['user_id'],
                    text=message,
                    parse_mode='Markdown'
                )
                sent += 1
            except:
                pass
        
        logger.info(f"✅ Идеи: {sent}/{len(users)}")
    
    except Exception as e:
        logger.error(f"Ошибка идей: {e}")

async def send_reminder():
    """Каждые 2 часа - напоминания"""
    if not _bot:
        return
    
    logger.info("📨 Отправка напоминаний...")
    
    db_pool = get_db_pool()
    if not db_pool:
        return
    
    try:
        async with db_pool.acquire() as conn:
            users = await conn.fetch(
                'SELECT user_id FROM notification_settings WHERE reminders = TRUE'
            )
        
        if not users:
            return
        
        reminders = [
            "💧 Попей воды!",
            "🧘 Время размяться!",
            "👀 Дай глазам отдохнуть",
            "💾 Сделай бэкап проекта!",
            "☕ Время для перерыва",
        ]
        
        hour = datetime.now(TIMEZONE).hour
        reminder = reminders[hour % len(reminders)]
        message = f"⏰ {reminder}\n\n💪 Твоё здоровье важнее дедлайнов!"
        
        sent = 0
        for user in users:
            try:
                await _bot.send_message(
                    chat_id=user['user_id'],
                    text=message,
                    parse_mode='Markdown'
                )
                sent += 1
            except:
                pass
        
        logger.info(f"✅ Напоминания: {sent}/{len(users)}")
    
    except Exception as e:
        logger.error(f"Ошибка напоминаний: {e}")

def run_async(coro):
    """Запуск корутины из синхронного контекста"""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        return loop.create_task(coro)
    except RuntimeError:
        return asyncio.run(coro)

async def setup_scheduler(bot):
    """Настройка планировщика"""
    global _bot
    _bot = bot
    
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    
    # 08:00 - Мотивация
    scheduler.add_job(
        lambda: run_async(send_motivation()),
        'cron',
        hour=8,
        minute=0,
        id='motivation'
    )
    
    # 09:00 - Идея
    scheduler.add_job(
        lambda: run_async(send_idea()),
        'cron',
        hour=9,
        minute=0,
        id='idea'
    )
    
    # Каждые 2 часа 10:00-20:00 - напоминания
    scheduler.add_job(
        lambda: run_async(send_reminder()),
        'cron',
        hour='10,12,14,16,18,20',
        minute=0,
        id='reminders'
    )
    
    scheduler.start()
    logger.info("📅 Планировщик настроен: 08:00, 09:00, каждые 2ч")
    
    return scheduler
