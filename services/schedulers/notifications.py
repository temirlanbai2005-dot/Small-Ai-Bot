"""
Планировщик ежедневных уведомлений
"""

import logging
import pytz
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot

from database.db import get_db_pool
from services.gemini_ai import generate_motivation, generate_project_idea

logger = logging.getLogger(__name__)

TIMEZONE = pytz.timezone('Europe/Moscow')

async def send_motivation(bot: Bot):
    """08:00 - Мотивация дня"""
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
            return
        
        motivation = await generate_motivation()
        message = f"🌅 **Доброе утро!**\n\n{motivation}\n\nОтличного дня! 🚀"
        
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user['user_id'],
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.warning(f"Не удалось отправить {user['user_id']}: {e}")
        
        logger.info(f"✅ Мотивация отправлена {len(users)} пользователям")
    
    except Exception as e:
        logger.error(f"Ошибка отправки мотивации: {e}")

async def send_idea(bot: Bot):
    """09:00 - Идея дня"""
    logger.info("📨 Отправка идеи дня...")
    
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
        
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user['user_id'],
                    text=message,
                    parse_mode='Markdown'
                )
            except:
                pass
        
        logger.info(f"✅ Идеи отправлены {len(users)} пользователям")
    
    except Exception as e:
        logger.error(f"Ошибка отправки идей: {e}")

async def send_reminder(bot: Bot):
    """Каждые 2 часа - напоминания"""
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
            "💧 Попей воды! Гидратация важна для продуктивности",
            "🧘 Время размяться! Встань и потянись 2 минуты",
            "👀 Дай глазам отдохнуть. Посмотри вдаль 20 секунд",
            "💾 Не забудь сделать бэкап проекта!",
            "☕ Время для короткого перерыва",
        ]
        
        hour = datetime.now(TIMEZONE).hour
        reminder = reminders[hour % len(reminders)]
        message = f"⏰ **Напоминание:**\n\n{reminder}\n\n💪 Твоё здоровье важнее дедлайнов!"
        
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user['user_id'],
                    text=message,
                    parse_mode='Markdown'
                )
            except:
                pass
        
        logger.info(f"✅ Напоминания отправлены {len(users)} пользователям")
    
    except Exception as e:
        logger.error(f"Ошибка отправки напоминаний: {e}")

async def setup_scheduler(bot: Bot):
    """Настройка и запуск планировщика"""
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    
    # 08:00 - Мотивация
    scheduler.add_job(
        send_motivation,
        CronTrigger(hour=8, minute=0, timezone=TIMEZONE),
        args=[bot],
        id='motivation_daily',
        replace_existing=True
    )
    
    # 09:00 - Идея дня
    scheduler.add_job(
        send_idea,
        CronTrigger(hour=9, minute=0, timezone=TIMEZONE),
        args=[bot],
        id='idea_daily',
        replace_existing=True
    )
    
    # Каждые 2 часа с 10:00 до 20:00 - напоминания
    scheduler.add_job(
        send_reminder,
        CronTrigger(hour='10,12,14,16,18,20', minute=0, timezone=TIMEZONE),
        args=[bot],
        id='reminders',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ Планировщик уведомлений настроен")
    
    return scheduler
