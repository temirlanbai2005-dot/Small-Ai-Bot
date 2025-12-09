"""
Планировщик ежедневных уведомлений
"""

import logging
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
from telegram.ext import Application

from config.settings import TELEGRAM_TOKEN, NOTIFICATION_TIMES, TIMEZONE
from database.db import get_db_pool
from services.gemini_ai import generate_motivation, generate_project_idea
from services.parsers.artstation import get_artstation_trends
from services.parsers.music_trends import get_music_trends

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone=TIMEZONE)

async def send_motivation_notification(bot: Bot):
    """08:00 - Мотивация дня + крутой арт"""
    logger.info("📨 Отправка мотивации дня...")
    
    db_pool = get_db_pool()
    if not db_pool:
        return
    
    try:
        # Получаем пользователей с включенными уведомлениями
        async with db_pool.acquire() as conn:
            users = await conn.fetch('''
                SELECT user_id 
                FROM notification_settings 
                WHERE motivation = TRUE
            ''')
        
        if not users:
            logger.info("Нет пользователей для мотивации")
            return
        
        # Генерируем мотивацию
        motivation = await generate_motivation()
        
        # Получаем случайный топ-арт
        arts = await get_artstation_trends(limit=1)
        art_info = ""
        if arts:
            art = arts[0]
            art_info = f"\n\n🎨 **Арт дня:**\n{art['title']} — {art['artist']}\n[Смотреть]({art['url']})"
        
        message = f"🌅 **Доброе утро!**\n\n{motivation}{art_info}"
        
        # Отправляем всем пользователям
        sent_count = 0
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user['user_id'],
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
                sent_count += 1
            except Exception as e:
                logger.warning(f"Ошибка отправки пользователю {user['user_id']}: {e}")
        
        logger.info(f"✅ Мотивация отправлена {sent_count} пользователям")
    
    except Exception as e:
        logger.error(f"Ошибка отправки мотивации: {e}")

async def send_idea_notification(bot: Bot):
    """09:00 - Идея дня для нового проекта"""
    logger.info("📨 Отправка идеи дня...")
    
    db_pool = get_db_pool()
    if not db_pool:
        return
    
    try:
        async with db_pool.acquire() as conn:
            users = await conn.fetch('''
                SELECT user_id 
                FROM notification_settings 
                WHERE idea = TRUE
            ''')
        
        if not users:
            return
        
        # Генерируем идею
        idea = await generate_project_idea()
        message = f"💡 **Идея дня для проекта:**\n\n{idea}\n\n🚀 Начни прямо сегодня!"
        
        sent_count = 0
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user['user_id'],
                    text=message,
                    parse_mode='Markdown'
                )
                sent_count += 1
            except Exception as e:
                logger.warning(f"Ошибка отправки идеи пользователю {user['user_id']}: {e}")
        
        logger.info(f"✅ Идеи отправлены {sent_count} пользователям")
    
    except Exception as e:
        logger.error(f"Ошибка отправки идей: {e}")

async def send_trends_notification(bot: Bot):
    """10:00 - Свежие тренды + музыка"""
    logger.info("📨 Отправка трендов...")
    
    db_pool = get_db_pool()
    if not db_pool:
        return
    
    try:
        async with db_pool.acquire() as conn:
            users = await conn.fetch('''
                SELECT user_id 
                FROM notification_settings 
                WHERE trends = TRUE
            ''')
        
        if not users:
            return
        
        # Получаем тренды
        art_trends = await get_artstation_trends(limit=5)
        music_trends = await get_music_trends(limit=10)
        
        # Формируем сообщение
        message = "🔥 **ТРЕНДЫ СЕГОДНЯ**\n\n"
        
        if art_trends:
            message += "🎨 **Топ-5 ArtStation:**\n"
            for i, art in enumerate(art_trends, 1):
                message += f"{i}. {art['title']} — {art['artist']}\n"
            message += "\n"
        
        if music_trends:
            message += "🎵 **Топ-10 музыки:**\n"
            for i, track in enumerate(music_trends[:10], 1):
                message += f"{i}. {track['title']} — {track['artist']}\n"
        
        message += "\n💡 Полные тренды: /trends"
        
        sent_count = 0
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user['user_id'],
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                sent_count += 1
            except Exception as e:
                logger.warning(f"Ошибка отправки трендов пользователю {user['user_id']}: {e}")
        
        logger.info(f"✅ Тренды отправлены {sent_count} пользователям")
    
    except Exception as e:
        logger.error(f"Ошибка отправки трендов: {e}")

async def send_jobs_notification(bot: Bot):
    """11:00 - Новые вакансии и фриланс-заказы"""
    logger.info("📨 Отправка вакансий...")
    
    db_pool = get_db_pool()
    if not db_pool:
        return
    
    try:
        async with db_pool.acquire() as conn:
            users = await conn.fetch('''
                SELECT user_id 
                FROM notification_settings 
                WHERE jobs = TRUE
            ''')
        
        if not users:
            return
        
        # Заглушка для вакансий (можно добавить парсинг ArtStation Jobs, Upwork и т.д.)
        message = """
💼 **Вакансии и фриланс**

🔍 **Где искать:**
• ArtStation Jobs
• Upwork - 3D Modeling
• Freelancer
• Fiverr
• LinkedIn Jobs

💡 **Совет дня:**
Обнови портфолио и добавь последние работы для лучших предложений!

🔗 [ArtStation Jobs](https://www.artstation.com/jobs)
        """
        
        sent_count = 0
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user['user_id'],
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                sent_count += 1
            except Exception as e:
                logger.warning(f"Ошибка отправки вакансий пользователю {user['user_id']}: {e}")
        
        logger.info(f"✅ Вакансии отправлены {sent_count} пользователям")
    
    except Exception as e:
        logger.error(f"Ошибка отправки вакансий: {e}")

async def send_assets_notification(bot: Bot):
    """12:00 - Топ ассетов/шейдеров недели"""
    logger.info("📨 Отправка топ ассетов...")
    
    db_pool = get_db_pool()
    if not db_pool:
        return
    
    try:
        async with db_pool.acquire() as conn:
            users = await conn.fetch('''
                SELECT user_id 
                FROM notification_settings 
                WHERE assets = TRUE
            ''')
        
        if not users:
            return
        
        # Заглушка для ассетов
        message = """
🎁 **Топ ассеты недели**

🆓 **Бесплатные ресурсы:**
• Quixel Megascans - новые материалы
• Poly Haven - HDRI и текстуры
• BlenderKit - 3D модели
• Substance Source - материалы

💎 **Платные must-have:**
• Gumroad - инди-ассеты
• Artstation Marketplace
• CGTrader

📚 Проверь обновления в своих библиотеках!
        """
        
        sent_count = 0
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user['user_id'],
                    text=message,
                    parse_mode='Markdown'
                )
                sent_count += 1
            except Exception as e:
                logger.warning(f"Ошибка отправки ассетов пользователю {user['user_id']}: {e}")
        
        logger.info(f"✅ Ассеты отправлены {sent_count} пользователям")
    
    except Exception as e:
        logger.error(f"Ошибка отправки ассетов: {e}")

async def send_reminder_notification(bot: Bot):
    """Каждые 2 часа - напоминания (вода, разминка, бэкап)"""
    logger.info("📨 Отправка напоминаний...")
    
    db_pool = get_db_pool()
    if not db_pool:
        return
    
    try:
        async with db_pool.acquire() as conn:
            users = await conn.fetch('''
                SELECT user_id 
                FROM notification_settings 
                WHERE reminders = TRUE
            ''')
        
        if not users:
            return
        
        # Варианты напоминаний
        reminders = [
            "💧 Попей воды!",
            "🧘 Время размяться! Встань и потянись 2 минуты",
            "💾 Не забудь сделать бэкап проекта!",
            "👀 Дай глазам отдохнуть. Посмотри вдаль 20 секунд",
            "☕ Время для короткого перерыва",
        ]
        
        # Выбираем в зависимости от часа
        hour = datetime.now().hour
        reminder_index = (hour // 2) % len(reminders)
        reminder = reminders[reminder_index]
        
        message = f"⏰ **Напоминание**\n\n{reminder}\n\nТвоё здоровье важнее дедлайнов! 💪"
        
        sent_count = 0
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user['user_id'],
                    text=message,
                    parse_mode='Markdown'
                )
                sent_count += 1
            except Exception as e:
                logger.warning(f"Ошибка отправки напоминания пользователю {user['user_id']}: {e}")
        
        logger.info(f"✅ Напоминания отправлены {sent_count} пользователям")
    
    except Exception as e:
        logger.error(f"Ошибка отправки напоминаний: {e}")

async def start_notification_scheduler(application: Application):
    """Запуск планировщика уведомлений"""
    bot = application.bot
    
    # Ежедневные уведомления
    scheduler.add_job(
        send_motivation_notification,
        CronTrigger(hour=NOTIFICATION_TIMES['motivation'], minute=0, timezone=TIMEZONE),
        args=[bot],
        id='motivation_daily'
    )
    
    scheduler.add_job(
        send_idea_notification,
        CronTrigger(hour=NOTIFICATION_TIMES['idea'], minute=0, timezone=TIMEZONE),
        args=[bot],
        id='idea_daily'
    )
    
    scheduler.add_job(
        send_trends_notification,
        CronTrigger(hour=NOTIFICATION_TIMES['trends'], minute=0, timezone=TIMEZONE),
        args=[bot],
        id='trends_daily'
    )
    
    scheduler.add_job(
        send_jobs_notification,
        CronTrigger(hour=NOTIFICATION_TIMES['jobs'], minute=0, timezone=TIMEZONE),
        args=[bot],
        id='jobs_daily'
    )
    
    scheduler.add_job(
        send_assets_notification,
        CronTrigger(hour=NOTIFICATION_TIMES['assets'], minute=0, timezone=TIMEZONE),
        args=[bot],
        id='assets_daily'
    )
    
    # Напоминания каждые 2 часа (с 8:00 до 22:00)
    scheduler.add_job(
        send_reminder_notification,
        CronTrigger(hour='8-22/2', minute=0, timezone=TIMEZONE),
        args=[bot],
        id='reminders_2h'
    )
    
    scheduler.start()
    logger.info("✅ Планировщик уведомлений запущен")
