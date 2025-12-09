"""
Telegram Bot для 3D-артистов
Главный файл запуска
"""

import os
import asyncio
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем переменные окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
PORT = int(os.getenv('PORT', 10000))

# Проверка обязательных переменных
if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN не установлен!")
    exit(1)

if not GEMINI_API_KEY:
    logger.error("❌ GEMINI_API_KEY не установлен!")
    exit(1)

if not DATABASE_URL:
    logger.error("❌ DATABASE_URL не установлен!")
    exit(1)

# Импорты модулей проекта
from database.db import init_db, close_db
from handlers.basic import start, help_command
from handlers.notes import add_note, show_notes, delete_note
from handlers.tasks import add_task, show_tasks, complete_task, delete_task
from handlers.ai import ask_ai
from handlers.stats import show_stats
from handlers.trends import show_trends, toggle_trends_notifications
from handlers.content_plan import (
    create_content_plan,
    schedule_post,
    view_scheduled_posts,
    edit_scheduled_post,
    delete_scheduled_post
)
from handlers.notifications import notification_settings, toggle_notification
from handlers.messages import handle_message

# Глобальные переменные
application = None

async def error_handler(update: Update, context):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")

async def post_init(app: Application):
    """Инициализация после запуска"""
    logger.info("🔧 Инициализация бота...")
    
    # Инициализация базы данных
    try:
        await init_db()
        logger.info("✅ База данных подключена!")
    except Exception as e:
        logger.error(f"❌ Ошибка БД: {e}")
    
    logger.info("✅ Бот инициализирован!")

# Health check
async def health_check(request):
    return web.Response(text="✅ Bot is running!", status=200)

async def run_web_server():
    """Запуск веб-сервера"""
    web_app = web.Application()
    web_app.router.add_get('/', health_check)
    web_app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"🌐 Веб-сервер запущен на порту {PORT}")
    return runner

async def main():
    """Главная функция"""
    global application
    
    # Запускаем веб-сервер
    web_runner = await run_web_server()
    
    # Создаём приложение бота
    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    application.add_handler(CommandHandler("note", add_note))
    application.add_handler(CommandHandler("notes", show_notes))
    application.add_handler(CommandHandler("delnote", delete_note))
    
    application.add_handler(CommandHandler("task", add_task))
    application.add_handler(CommandHandler("tasks", show_tasks))
    application.add_handler(CommandHandler("complete", complete_task))
    application.add_handler(CommandHandler("deltask", delete_task))
    
    application.add_handler(CommandHandler("ask", ask_ai))
    application.add_handler(CommandHandler("stats", show_stats))
    
    application.add_handler(CommandHandler("trends", show_trends))
    application.add_handler(CommandHandler("trendsnotify", toggle_trends_notifications))
    
    application.add_handler(CommandHandler("contentplan", create_content_plan))
    application.add_handler(CommandHandler("schedule", schedule_post))
    application.add_handler(CommandHandler("scheduled", view_scheduled_posts))
    application.add_handler(CommandHandler("editpost", edit_scheduled_post))
    application.add_handler(CommandHandler("delpost", delete_scheduled_post))
    
    application.add_handler(CommandHandler("notifications", notification_settings))
    application.add_handler(CommandHandler("togglenotif", toggle_notification))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.add_error_handler(error_handler)
    
    # Запуск бота через run_polling (правильный способ)
    logger.info("🤖 Запуск бота...")
    
    async with application:
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        
        logger.info("✅ Бот успешно запущен!")
        
        # Запускаем планировщик ПОСЛЕ запуска бота
        try:
            from services.schedulers.notifications import setup_scheduler
            scheduler = await setup_scheduler(application.bot)
            logger.info("✅ Планировщик запущен!")
        except Exception as e:
            logger.warning(f"⚠️ Планировщик не запущен: {e}")
        
        # Держим бота запущенным
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
