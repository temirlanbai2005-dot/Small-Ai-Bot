"""
Telegram Bot для 3D-артистов
"""

import os
import asyncio
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Логирование
logging.basicConfig(
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Переменные окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
PORT = int(os.getenv('PORT', 10000))

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не установлен!")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY не установлен!")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не установлен!")

# Импорты
from database.db import init_db
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

# Health check
async def health_check(request):
    return web.Response(text="OK", status=200)

async def run_webserver():
    """Веб-сервер для Render"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"🌐 Веб-сервер на порту {PORT}")

async def error_handler(update, context):
    logger.error(f"Ошибка: {context.error}")

async def on_startup(app: Application):
    """При запуске бота"""
    logger.info("🔧 Инициализация...")
    try:
        await init_db()
        logger.info("✅ БД подключена!")
    except Exception as e:
        logger.error(f"❌ Ошибка БД: {e}")

def main():
    """Главная функция"""
    
    # Создаём event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Запускаем веб-сервер
    loop.run_until_complete(run_webserver())
    
    # Создаём бота
    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(on_startup)
        .build()
    )
    
    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("note", add_note))
    app.add_handler(CommandHandler("notes", show_notes))
    app.add_handler(CommandHandler("delnote", delete_note))
    app.add_handler(CommandHandler("task", add_task))
    app.add_handler(CommandHandler("tasks", show_tasks))
    app.add_handler(CommandHandler("complete", complete_task))
    app.add_handler(CommandHandler("deltask", delete_task))
    app.add_handler(CommandHandler("ask", ask_ai))
    app.add_handler(CommandHandler("stats", show_stats))
    app.add_handler(CommandHandler("trends", show_trends))
    app.add_handler(CommandHandler("trendsnotify", toggle_trends_notifications))
    app.add_handler(CommandHandler("contentplan", create_content_plan))
    app.add_handler(CommandHandler("schedule", schedule_post))
    app.add_handler(CommandHandler("scheduled", view_scheduled_posts))
    app.add_handler(CommandHandler("editpost", edit_scheduled_post))
    app.add_handler(CommandHandler("delpost", delete_scheduled_post))
    app.add_handler(CommandHandler("notifications", notification_settings))
    app.add_handler(CommandHandler("togglenotif", toggle_notification))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    # Запуск
    logger.info("🤖 Запуск бота...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
