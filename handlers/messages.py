"""
Обработчик текстовых сообщений и кнопок меню
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from database.db import update_user_stats
from services.gemini_ai import ask_gemini, generate_art_idea
from handlers.stats import show_stats
from handlers.trends import show_trends

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    text = update.message.text
    
    # Обработка кнопок меню
    if text == "💬 Спросить AI":
        await update.message.reply_text(
            "Задайте вопрос AI:\n"
            "`/ask <ваш вопрос>`\n\n"
            "Или просто напишите свой вопрос без команды!",
            parse_mode='Markdown'
        )
    
    elif text == "📝 Заметка":
        await update.message.reply_text(
            "📝 **Заметки:**\n\n"
            "`/note <текст>` — добавить\n"
            "`/notes` — показать все\n"
            "`/delnote <номер>` — удалить",
            parse_mode='Markdown'
        )
    
    elif text == "✅ Задачи":
        await update.message.reply_text(
            "✅ **Задачи:**\n\n"
            "`/task <описание>` — добавить\n"
            "`/tasks` — показать все\n"
            "`/complete <номер>` — выполнить\n"
            "`/deltask <номер>` — удалить",
            parse_mode='Markdown'
        )
    
    elif text == "🎨 Идея для арта":
        await update.message.reply_text("🎨 Генерирую креативную идею...")
        try:
            idea = await generate_art_idea()
            await update.message.reply_text(f"💡 **Идея для арта:**\n\n{idea}", parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Ошибка генерации идеи: {e}")
            await update.message.reply_text("❌ Ошибка генерации. Попробуйте позже.")
    
    elif text == "🔥 Тренды":
        await show_trends(update, context)
    
    elif text == "📅 Контент-план":
        await update.message.reply_text(
            "📅 **Контент-план:**\n\n"
            "`/contentplan` — сгенерировать идею\n"
            "`/schedule` — запланировать пост\n"
            "`/scheduled` — календарь постов",
            parse_mode='Markdown'
        )
    
    elif text == "⏰ Уведомления":
        from handlers.notifications import notification_settings
        await notification_settings(update, context)
    
    elif text == "📊 Статистика":
        await show_stats(update, context)
    
    elif text == "ℹ️ Помощь":
        from handlers.basic import help_command
        await help_command(update, context)
    
    else:
        # Любой другой текст отправляем в AI
        await update.message.reply_text("🤔 Обрабатываю...")
        try:
            response = await ask_gemini(text)
            
            # Разбиваем длинные ответы
            if len(response) > 4096:
                for i in range(0, len(response), 4096):
                    await update.message.reply_text(response[i:i+4096])
            else:
                await update.message.reply_text(f"🤖 {response}")
        except Exception as e:
            logger.error(f"Ошибка AI: {e}")
            await update.message.reply_text("❌ Ошибка AI. Попробуйте переформулировать вопрос.")
