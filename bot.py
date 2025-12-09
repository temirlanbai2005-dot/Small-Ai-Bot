import os
import asyncio
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Импорты из нашей структуры
from config.settings import TELEGRAM_TOKEN, PORT
from database.db import init_db, close_db
from utils.logger import setup_logger
from utils.keyboards import get_main_keyboard

# Импорт обработчиков команд
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

# Импорт планировщиков
from services.schedulers.notifications import start_notification_scheduler
from services.schedulers.trends import start_trends_scheduler
from services.schedulers.auto_posting import start_autoposting_scheduler

# Настройка логирования
logger = setup_logger()

# Обработчик ошибок
async def error_handler(update: Update, context):
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)

# Инициализация после запуска приложения
async def post_init(application: Application):
    """Вызывается после инициализации приложения"""
    logger.info("🔧 Инициализация бота...")
    
    # Инициализация базы данных
    await init_db()
    
    # Запуск планировщиков
    await start_notification_scheduler(application)
    await start_trends_scheduler(application)
    await start_autoposting_scheduler(application)
    
    logger.info("✅ Бот полностью инициализирован!")

# Закрытие ресурсов
async def post_shutdown(application: Application):
    """Вызывается при остановке бота"""
    logger.info("🔄 Завершение работы бота...")
    await close_db()
    logger.info("✅ Ресурсы освобождены")

# Health check для Render
async def health_check(request):
    """Эндпоинт для проверки здоровья сервиса"""
    return web.Response(text="✅ Bot is running! 🤖", status=200)

async def start_web_server():
    """Запускает веб-сервер для Render"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"🌐 Веб-сервер запущен на порту {PORT}")

async def run_bot():
    """Запускает Telegram бота"""
    # Создание приложения
    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    
    # ========== БАЗОВЫЕ КОМАНДЫ ==========
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # ========== ЗАМЕТКИ ==========
    application.add_handler(CommandHandler("note", add_note))
    application.add_handler(CommandHandler("notes", show_notes))
    application.add_handler(CommandHandler("delnote", delete_note))
    
    # ========== ЗАДАЧИ ==========
    application.add_handler(CommandHandler("task", add_task))
    application.add_handler(CommandHandler("tasks", show_tasks))
    application.add_handler(CommandHandler("complete", complete_task))
    application.add_handler(CommandHandler("deltask", delete_task))
    
    # ========== AI ==========
    application.add_handler(CommandHandler("ask", ask_ai))
    
    # ========== СТАТИСТИКА ==========
    application.add_handler(CommandHandler("stats", show_stats))
    
    # ========== ТРЕНДЫ (НОВОЕ!) ==========
    application.add_handler(CommandHandler("trends", show_trends))
    application.add_handler(CommandHandler("trendsnotify", toggle_trends_notifications))
    
    # ========== КОНТЕНТ-ПЛАН (НОВОЕ!) ==========
    application.add_handler(CommandHandler("contentplan", create_content_plan))
    application.add_handler(CommandHandler("schedule", schedule_post))
    application.add_handler(CommandHandler("scheduled", view_scheduled_posts))
    application.add_handler(CommandHandler("editpost", edit_scheduled_post))
    application.add_handler(CommandHandler("delpost", delete_scheduled_post))
    
    # ========== УВЕДОМЛЕНИЯ (НОВОЕ!) ==========
    application.add_handler(CommandHandler("notifications", notification_settings))
    application.add_handler(CommandHandler("togglenotif", toggle_notification))
    
    # ========== ОБРАБОТКА ТЕКСТА ==========
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # ========== ОБРАБОТЧИК ОШИБОК ==========
    application.add_error_handler(error_handler)
    
    # Запуск бота
    logger.info("🤖 Запуск Telegram бота...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )
    
    # Держим бота запущенным
    logger.info("✅ Бот успешно запущен и работает!")
    while True:
        await asyncio.sleep(1)

def main():
    """Главная функция"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Запускаем веб-сервер и бота параллельно
        loop.run_until_complete(start_web_server())
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        logger.info("⚠️ Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
    finally:
        loop.close()
        logger.info("👋 Бот остановлен")

if __name__ == '__main__':
    main()
