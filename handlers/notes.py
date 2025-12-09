"""
Обработчики для работы с заметками
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_db_pool, update_user_stats

logger = logging.getLogger(__name__)

async def add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить заметку: /note <текст>"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    if not context.args:
        await update.message.reply_text(
            "❌ Использование: `/note <текст заметки>`\n\n"
            "Пример: `/note Изучить Substance Designer`",
            parse_mode='Markdown'
        )
        return
    
    db_pool = get_db_pool()
    if not db_pool:
        await update.message.reply_text("❌ База данных недоступна. Попробуйте через минуту.")
        return
    
    note_text = ' '.join(context.args)
    
    try:
        async with db_pool.acquire() as conn:
            note_id = await conn.fetchval(
                'INSERT INTO notes (user_id, text) VALUES ($1, $2) RETURNING id',
                user.id, note_text
            )
        
        await update.message.reply_text(
            f"✅ **Заметка #{note_id} сохранена!**\n\n"
            f"📝 {note_text}\n\n"
            f"Посмотреть все: /notes",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Ошибка сохранения заметки: {e}")
        await update.message.reply_text("❌ Ошибка сохранения заметки")

async def show_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать все заметки: /notes"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    db_pool = get_db_pool()
    if not db_pool:
        await update.message.reply_text("❌ База данных недоступна.")
        return
    
    try:
        async with db_pool.acquire() as conn:
            notes = await conn.fetch(
                'SELECT id, text, created_at FROM notes WHERE user_id = $1 ORDER BY created_at DESC',
                user.id
            )
        
        if not notes:
            await update.message.reply_text(
                "📝 У вас пока нет заметок\n\n"
                "Добавить: `/note <текст>`",
                parse_mode='Markdown'
            )
            return
        
        notes_text = f"📝 **Ваши заметки ({len(notes)}):**\n\n"
        
        for note in notes:
            date_str = note['created_at'].strftime("%d.%m.%Y %H:%M")
            # Обрезаем длинные заметки
            text_preview = note['text'][:100] + '...' if len(note['text']) > 100 else note['text']
            notes_text += f"**#{note['id']}** {text_preview}\n📅 {date_str}\n\n"
        
        notes_text += "💡 Удалить: `/delnote <номер>`"
        
        # Если текст слишком длинный, разбиваем на части
        if len(notes_text) > 4096:
            for i in range(0, len(notes_text), 4096):
                await update.message.reply_text(notes_text[i:i+4096], parse_mode='Markdown')
        else:
            await update.message.reply_text(notes_text, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Ошибка получения заметок: {e}")
        await update.message.reply_text("❌ Ошибка получения заметок")

async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить заметку: /delnote <id>"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    if not context.args:
        await update.message.reply_text(
            "❌ Использование: `/delnote <номер>`\n\n"
            "Пример: `/delnote 5`",
            parse_mode='Markdown'
        )
        return
    
    db_pool = get_db_pool()
    if not db_pool:
        await update.message.reply_text("❌ База данных недоступна.")
        return
    
    try:
        note_id = int(context.args[0])
        
        async with db_pool.acquire() as conn:
            result = await conn.execute(
                'DELETE FROM notes WHERE id = $1 AND user_id = $2',
                note_id, user.id
            )
        
        if result == "DELETE 1":
            await update.message.reply_text(f"✅ Заметка **#{note_id}** удалена!", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Заметка **#{note_id}** не найдена", parse_mode='Markdown')
            
    except ValueError:
        await update.message.reply_text("❌ Неверный номер заметки. Используйте число.")
    except Exception as e:
        logger.error(f"Ошибка удаления заметки: {e}")
        await update.message.reply_text("❌ Ошибка удаления заметки")
