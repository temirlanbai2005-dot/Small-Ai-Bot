"""
Обработчики для трендов (ArtStation + музыка)
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_db_pool, update_user_stats
from services.parsers.artstation import get_artstation_trends
from services.parsers.music_trends import get_music_trends

logger = logging.getLogger(__name__)

async def show_trends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать актуальные тренды: /trends"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    await update.message.reply_text("🔥 Загружаю свежие тренды...")
    
    try:
        # Получаем тренды с ArtStation
        art_trends = await get_artstation_trends(limit=10)
        
        # Получаем музыкальные тренды
        music_trends = await get_music_trends(limit=20)
        
        # Формируем сообщение
        message = "🔥 **АКТУАЛЬНЫЕ ТРЕНДЫ**\n\n"
        
        # ArtStation тренды
        if art_trends:
            message += "🎨 **Топ-10 трендов ArtStation:**\n\n"
            for i, art in enumerate(art_trends, 1):
                message += f"{i}. **{art['title']}**\n"
                message += f"   👤 {art['artist']}\n"
                message += f"   ❤️ {art['likes']} | 👁 {art['views']}\n"
                if art.get('url'):
                    message += f"   🔗 [Смотреть]({art['url']})\n"
                message += "\n"
        else:
            message += "🎨 ArtStation тренды временно недоступны\n\n"
        
        # Музыкальные тренды
        if music_trends:
            message += "🎵 **Топ-20 треков TikTok/Billboard:**\n\n"
            for i, track in enumerate(music_trends[:10], 1):  # Показываем первые 10
                message += f"{i}. **{track['title']}** — {track['artist']}\n"
            
            message += "\n_...и ещё 10 треков_\n\n"
        else:
            message += "🎵 Музыкальные тренды временно недоступны\n\n"
        
        message += "💡 Автоматическая рассылка: /trendsnotify"
        
        # Разбиваем если слишком длинное
        if len(message) > 4096:
            parts = [message[i:i+4096] for i in range(0, len(message), 4096)]
            for part in parts:
                await update.message.reply_text(part, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Ошибка получения трендов: {e}")
        await update.message.reply_text(
            "❌ Ошибка загрузки трендов.\n"
            "Попробуйте позже или проверьте подключение."
        )

async def toggle_trends_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Включить/выключить ежедневные уведомления о трендах"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    db_pool = get_db_pool()
    if not db_pool:
        await update.message.reply_text("❌ База данных недоступна.")
        return
    
    try:
        async with db_pool.acquire() as conn:
            # Проверяем текущее состояние
            current_state = await conn.fetchval(
                'SELECT trends FROM notification_settings WHERE user_id = $1',
                user.id
            )
            
            if current_state is None:
                # Создаем настройки если их нет
                await conn.execute(
                    'INSERT INTO notification_settings (user_id, trends) VALUES ($1, TRUE)',
                    user.id
                )
                new_state = True
            else:
                # Переключаем состояние
                new_state = not current_state
                await conn.execute(
                    'UPDATE notification_settings SET trends = $1 WHERE user_id = $2',
                    new_state, user.id
                )
        
        if new_state:
            await update.message.reply_text(
                "✅ **Ежедневные тренды включены!**\n\n"
                "Каждый день в 10:00 вы будете получать свежие тренды с ArtStation и музыку из TikTok.\n\n"
                "Отключить: /trendsnotify",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ **Ежедневные тренды отключены**\n\n"
                "Включить обратно: /trendsnotify",
                parse_mode='Markdown'
            )
    
    except Exception as e:
        logger.error(f"Ошибка переключения уведомлений: {e}")
        await update.message.reply_text("❌ Ошибка изменения настроек")
