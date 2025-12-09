"""
Обработчики для работы с задачами
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_db_pool, update_user_stats
from datetime import datetime

logger = logging.getLogger(__name__)

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить задачу: /task <описание>"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    if not context.args:
        await update.message.reply_text(
            "❌ Использование: `/task <описание задачи>`\n\n"
            "Пример: `/task Доделать текстуры персонажа`",
            parse_mode='Markdown'
        )
        return
    
    db_pool = get_db_pool()
    if not db_pool:
        await update.message.reply_text("❌ База данных недоступна.")
        return
    
    task_text = ' '.join(context.args)
    
    try:
        async with db_pool.acquire() as conn:
            task_id = await conn.fetchval(
                'INSERT INTO tasks (user_id, text) VALUES ($1, $2) RETURNING id',
                user.id, task_text
            )
        
        await update.message.reply_text(
            f"✅ **Задача #{task_id} добавлена!**\n\n"
            f"📋 {task_text}\n\n"
            f"Посмотреть все: /tasks",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Ошибка добавления задачи: {e}")
        await update.message.reply_text("❌ Ошибка добавления задачи")

async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать все задачи: /tasks"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    db_pool = get_db_pool()
    if not db_pool:
        await update.message.reply_text("❌ База данных недоступна.")
        return
    
    try:
        async with db_pool.acquire() as conn:
            tasks = await conn.fetch(
                'SELECT id, text, completed, created_at FROM tasks WHERE user_id = $1 ORDER BY completed, created_at DESC',
                user.id
            )
        
        if not tasks:
            await update.message.reply_text(
                "📋 У вас пока нет задач\n\n"
                "Добавить: `/task <описание>`",
                parse_mode='Markdown'
            )
            return
        
        active_tasks = [t for t in tasks if not t['completed']]
        completed_tasks = [t for t in tasks if t['completed']]
        
        tasks_text = f"📋 **Ваши задачи:**\n\n"
        
        if active_tasks:
            tasks_text += "⏳ **Активные:**\n"
            for task in active_tasks:
                date_str = task['created_at'].strftime("%d.%m.%Y")
                text_preview = task['text'][:80] + '...' if len(task['text']) > 80 else task['text']
                tasks_text += f"**#{task['id']}** {text_preview}\n📅 {date_str}\n\n"
        
        if completed_tasks:
            tasks_text += "✅ **Выполненные:**\n"
            for task in completed_tasks[:5]:  # Показываем только последние 5
                text_preview = task['text'][:60] + '...' if len(task['text']) > 60 else task['text']
                tasks_text += f"~~#{task['id']} {text_preview}~~\n\n"
        
        tasks_text += "\n💡 **Команды:**\n"
        tasks_text += "`/complete <номер>` — отметить выполненной\n"
        tasks_text += "`/deltask <номер>` — удалить"
        
        await update.message.reply_text(tasks_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка получения задач: {e}")
        await update.message.reply_text("❌ Ошибка получения задач")

async def complete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отметить задачу выполненной: /complete <id>"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    if not context.args:
        await update.message.reply_text(
            "❌ Использование: `/complete <номер задачи>`\n\n"
            "Пример: `/complete 3`",
            parse_mode='Markdown'
        )
        return
    
    db_pool = get_db_pool()
    if not db_pool:
        await update.message.reply_text("❌ База данных недоступна.")
        return
    
    try:
        task_id = int(context.args[0])
        
        async with db_pool.acquire() as conn:
            result = await conn.execute(
                'UPDATE tasks SET completed = TRUE WHERE id = $1 AND user_id = $2',
                task_id, user.id
            )
        
        if result == "UPDATE 1":
            await update.message.reply_text(
                f"✅ **Задача #{task_id} выполнена!**\n\n"
                f"Отличная работа! 🎉",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(f"❌ Задача **#{task_id}** не найдена", parse_mode='Markdown')
            
    except ValueError:
        await update.message.reply_text("❌ Неверный номер задачи. Используйте число.")
    except Exception as e:
        logger.error(f"Ошибка обновления задачи: {e}")
        await update.message.reply_text("❌ Ошибка обновления задачи")

async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить задачу: /deltask <id>"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    if not context.args:
        await update.message.reply_text(
            "❌ Использование: `/deltask <номер>`\n\n"
            "Пример: `/deltask 3`",
            parse_mode='Markdown'
        )
        return
    
    db_pool = get_db_pool()
    if not db_pool:
        await update.message.reply_text("❌ База данных недоступна.")
        return
    
    try:
        task_id = int(context.args[0])
        
        async with db_pool.acquire() as conn:
            result = await conn.execute(
                'DELETE FROM tasks WHERE id = $1 AND user_id = $2',
                task_id, user.id
            )
        
        if result == "DELETE 1":
            await update.message.reply_text(f"✅ Задача **#{task_id}** удалена!", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Задача **#{task_id}** не найдена", parse_mode='Markdown')
            
    except ValueError:
        await update.message.reply_text("❌ Неверный номер задачи.")
    except Exception as e:
        logger.error(f"Ошибка удаления задачи: {e}")
        await update.message.reply_text("❌ Ошибка удаления задачи")
