"""
Обработчик статистики пользователя
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_db_pool, update_user_stats

logger = logging.getLogger(__name__)

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику: /stats"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    db_pool = get_db_pool()
    if not db_pool:
        await update.message.reply_text("❌ База данных недоступна.")
        return
    
    try:
        async with db_pool.acquire() as conn:
            # Статистика пользователя
            stats = await conn.fetchrow(
                'SELECT total_messages, last_active, created_at FROM user_stats WHERE user_id = $1',
                user.id
            )
            
            # Количество заметок
            notes_count = await conn.fetchval(
                'SELECT COUNT(*) FROM notes WHERE user_id = $1',
                user.id
            )
            
            # Количество задач
            tasks_total = await conn.fetchval(
                'SELECT COUNT(*) FROM tasks WHERE user_id = $1',
                user.id
            )
            
            tasks_completed = await conn.fetchval(
                'SELECT COUNT(*) FROM tasks WHERE user_id = $1 AND completed = TRUE',
                user.id
            )
            
            tasks_active = tasks_total - tasks_completed
            
            # Запланированные посты
            scheduled_posts = await conn.fetchval(
                'SELECT COUNT(*) FROM scheduled_posts WHERE user_id = $1 AND status = $2',
                user.id, 'pending'
            )
            
            # Опубликованные посты
            posted_count = await conn.fetchval(
                'SELECT COUNT(*) FROM post_history WHERE user_id = $1',
                user.id
            )
        
        if not stats:
            await update.message.reply_text("📊 Статистика пока не собрана. Используйте бота активнее!")
            return
        
        # Вычисляем процент выполненных задач
        completion_rate = (tasks_completed / tasks_total * 100) if tasks_total > 0 else 0
        
        # Дни использования
        days_using = (stats['last_active'] - stats['created_at']).days + 1
        
        stats_text = f"""
📊 **Твоя статистика**

👤 **Пользователь:** {user.first_name}
🆔 **ID:** `{user.id}`

📈 **Активность:**
💬 Всего сообщений: **{stats['total_messages']}**
📅 Дней использования: **{days_using}**
⏰ Последняя активность: {stats['last_active'].strftime("%d.%m.%Y %H:%M")}

📝 **Заметки и задачи:**
📝 Заметок сохранено: **{notes_count}**
📋 Задач всего: **{tasks_total}**
⏳ Активных: **{tasks_active}**
✅ Выполнено: **{tasks_completed}** ({completion_rate:.0f}%)

📅 **Контент-план:**
⏰ Запланировано постов: **{scheduled_posts}**
✅ Опубликовано всего: **{posted_count}**

{"🔥 Отличная продуктивность!" if completion_rate > 50 else "💪 Продолжай в том же духе!"}
        """
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        await update.message.reply_text("❌ Ошибка получения статистики")
