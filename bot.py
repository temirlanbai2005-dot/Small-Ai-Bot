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

# Настройка базового логирования (до импорта других модулей)
logging.basicConfig(
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем переменные окружения напрямую
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
from utils.keyboards import get_main_keyboard

# Глобальная переменная для application
app = None

async def error_handler(update: Update, context):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")

async def post_init(application: Application):
    """Инициализация после запуска"""
    logger.info("🔧 Инициализация бота...")
    
    # Инициализация базы данных
    await init_db()
    
    logger.info("✅ Бот полностью инициализирован!")

# Health check для Render
async def health_check(request):
    """Эндпоинт для проверки здоровья"""
    return web.Response(text="✅ Bot is running! 🤖", status=200)

async def run_web_server():
    """Запуск веб-сервера"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"🌐 Веб-сервер запущен на порту {PORT}")

async def run_bot():
    """Запуск Telegram бота"""
    global app
    
    # Создание приложения
    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )
    
    # ========== БАЗОВЫЕ КОМАНДЫ ==========
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # ========== ЗАМЕТКИ ==========
    app.add_handler(CommandHandler("note", add_note))
    app.add_handler(CommandHandler("notes", show_notes))
    app.add_handler(CommandHandler("delnote", delete_note))
    
    # ========== ЗАДАЧИ ==========
    app.add_handler(CommandHandler("task", add_task))
    app.add_handler(CommandHandler("tasks", show_tasks))
    app.add_handler(CommandHandler("complete", complete_task))
    app.add_handler(CommandHandler("deltask", delete_task))
    
    # ========== AI ==========
    app.add_handler(CommandHandler("ask", ask_ai))
    
    # ========== СТАТИСТИКА ==========
    app.add_handler(CommandHandler("stats", show_stats))
    
    # ========== ТРЕНДЫ ==========
    app.add_handler(CommandHandler("trends", show_trends))
    app.add_handler(CommandHandler("trendsnotify", toggle_trends_notifications))
    
    # ========== КОНТЕНТ-ПЛАН ==========
    app.add_handler(CommandHandler("contentplan", create_content_plan))
    app.add_handler(CommandHandler("schedule", schedule_post))
    app.add_handler(CommandHandler("scheduled", view_scheduled_posts))
    app.add_handler(CommandHandler("editpost", edit_scheduled_post))
    app.add_handler(CommandHandler("delpost", delete_scheduled_post))
    
    # ========== УВЕДОМЛЕНИЯ ==========
    app.add_handler(CommandHandler("notifications", notification_settings))
    app.add_handler(CommandHandler("togglenotif", toggle_notification))
    
    # ========== ОБРАБОТКА ТЕКСТА ==========
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # ========== ОБРАБОТЧИК ОШИБОК ==========
    app.add_error_handler(error_handler)
    
    # Запуск бота
    logger.info("🤖 Запуск Telegram бота...")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )
    
    logger.info("✅ Бот успешно запущен и работает!")

async def main():
    """Главная функция"""
    # Запускаем веб-сервер
    await run_web_server()
    
    # Запускаем бота
    await run_bot()
    
    # Держим приложение запущенным
    try:
        while True:
            await asyncio.sleep(3600)  # Спим 1 час
    except asyncio.CancelledError:
        logger.info("⚠️ Получен сигнал остановки")
    finally:
        if app:
            await app.stop()
            await app.shutdown()
        await close_db()
        logger.info("👋 Бот остановлен")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ Остановка по Ctrl+C")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
