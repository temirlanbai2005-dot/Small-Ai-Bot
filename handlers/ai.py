"""
Обработчики для работы с AI (Google Gemini)
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from database.db import update_user_stats
from services.gemini_ai import ask_gemini, generate_art_idea

logger = logging.getLogger(__name__)

async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Спросить AI: /ask <вопрос>"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    if not context.args:
        await update.message.reply_text(
            "❌ Использование: `/ask <ваш вопрос>`\n\n"
            "Пример: `/ask Как улучшить топологию модели?`",
            parse_mode='Markdown'
        )
        return
    
    question = ' '.join(context.args)
    await update.message.reply_text("🤔 Думаю...")
    
    try:
        response = await ask_gemini(question)
        
        # Разбиваем длинные ответы
        if len(response) > 4096:
            for i in range(0, len(response), 4096):
                await update.message.reply_text(response[i:i+4096])
        else:
            await update.message.reply_text(f"🤖 {response}")
            
    except Exception as e:
        logger.error(f"Ошибка Gemini API: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при обращении к AI.\n"
            "Попробуйте позже или переформулируйте вопрос."
        )

async def generate_art_idea_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация идеи для арта"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    await update.message.reply_text("🎨 Генерирую креативную идею...")
    
    try:
        idea = await generate_art_idea()
        await update.message.reply_text(f"💡 **Идея для арта:**\n\n{idea}", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка генерации идеи: {e}")
        await update.message.reply_text("❌ Ошибка генерации идеи. Попробуйте позже.")
