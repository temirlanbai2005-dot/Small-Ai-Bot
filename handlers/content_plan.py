"""
Обработчики для контент-плана и автопостинга
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_db_pool, update_user_stats
from services.post_generator import generate_post_idea, generate_full_post
from services.translator import translate_to_russian
from config.platforms import SUPPORTED_PLATFORMS, get_platform_config
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

async def create_content_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создать идею для поста: /contentplan [платформа]"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    # Определяем платформу
    platform = ' '.join(context.args) if context.args else None
    
    if platform and platform not in SUPPORTED_PLATFORMS:
        await update.message.reply_text(
            f"❌ Неизвестная платформа: {platform}\n\n"
            f"Доступные платформы:\n" + "\n".join([f"• {p}" for p in SUPPORTED_PLATFORMS]),
            parse_mode='Markdown'
        )
        return
    
    await update.message.reply_text("🧠 Генерирую идею поста...")
    
    try:
        # Генерируем идею
        idea = await generate_post_idea(platform)
        
        # Генерируем полный пост на английском
        post_en = await generate_full_post(idea, platform)
        
        # Переводим на русский
        post_ru = await translate_to_russian(post_en)
        
        platform_info = get_platform_config(platform) if platform else {}
        
        message = f"💡 **Идея для поста**\n\n"
        
        if platform:
            message += f"📱 **Платформа:** {platform_info.get('emoji', '📱')} {platform}\n\n"
        
        message += f"🇬🇧 **English version:**\n{post_en}\n\n"
        message += f"🇷🇺 **Русская версия:**\n{post_ru}\n\n"
        message += f"💡 **Запланировать:** `/schedule {platform or 'Instagram'} <дата> <время>`\n"
        message += f"Пример: `/schedule Instagram 25.12.2024 15:00`"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка генерации контент-плана: {e}")
        await update.message.reply_text("❌ Ошибка генерации идеи. Попробуйте позже.")

async def schedule_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запланировать пост: /schedule <платформа> <дата> <время> <текст>"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    if len(context.args) < 4:
        await update.message.reply_text(
            "❌ Использование:\n"
            "`/schedule <платформа> <дата> <время> <текст поста>`\n\n"
            "Пример:\n"
            "`/schedule Instagram 25.12.2024 15:00 Мой новый 3D арт!`",
            parse_mode='Markdown'
        )
        return
    
    platform = context.args[0]
    date_str = context.args[1]
    time_str = context.args[2]
    content_ru = ' '.join(context.args[3:])
    
    # Валидация платформы
    if platform not in SUPPORTED_PLATFORMS:
        await update.message.reply_text(f"❌ Неизвестная платформа: {platform}")
        return
    
    try:
        # Парсим дату и время
        scheduled_datetime = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
        
        # Проверяем что дата в будущем
        if scheduled_datetime < datetime.now():
            await update.message.reply_text("❌ Дата должна быть в будущем!")
            return
        
        # Переводим на английский
        content_en = await translate_to_russian(content_ru, to_russian=False)
        
        db_pool = get_db_pool()
        async with db_pool.acquire() as conn:
            post_id = await conn.fetchval('''
                INSERT INTO scheduled_posts (user_id, platform, content_ru, content_en, scheduled_time)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            ''', user.id, platform, content_ru, content_en, scheduled_datetime)
        
        await update.message.reply_text(
            f"✅ **Пост #{post_id} запланирован!**\n\n"
            f"📱 Платформа: {platform}\n"
            f"📅 Дата: {scheduled_datetime.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"📝 Текст:\n{content_ru}\n\n"
            f"Посмотреть все: /scheduled",
            parse_mode='Markdown'
        )
        
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат даты/времени!\n"
            "Используйте: `ДД.ММ.ГГГГ ЧЧ:ММ`",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Ошибка планирования поста: {e}")
        await update.message.reply_text("❌ Ошибка планирования поста")

async def view_scheduled_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Посмотреть запланированные посты: /scheduled"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    db_pool = get_db_pool()
    if not db_pool:
        await update.message.reply_text("❌ База данных недоступна.")
        return
    
    try:
        async with db_pool.acquire() as conn:
            posts = await conn.fetch('''
                SELECT id, platform, content_ru, scheduled_time, status
                FROM scheduled_posts
                WHERE user_id = $1 AND status = 'pending'
                ORDER BY scheduled_time ASC
            ''', user.id)
        
        if not posts:
            await update.message.reply_text(
                "📅 У вас нет запланированных постов\n\n"
                "Создать: /contentplan\n"
                "Запланировать: /schedule",
                parse_mode='Markdown'
            )
            return
        
        message = f"📅 **Ваши запланированные посты ({len(posts)}):**\n\n"
        
        for post in posts:
            content_preview = post['content_ru'][:60] + '...' if len(post['content_ru']) > 60 else post['content_ru']
            time_str = post['scheduled_time'].strftime("%d.%m.%Y %H:%M")
            
            message += f"**#{post['id']}** {post['platform']}\n"
            message += f"📅 {time_str}\n"
            message += f"📝 {content_preview}\n\n"
        
        message += "💡 **Команды:**\n"
        message += "`/editpost <id>` — редактировать\n"
        message += "`/delpost <id>` — удалить"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка получения постов: {e}")
        await update.message.reply_text("❌ Ошибка получения постов")

async def edit_scheduled_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Редактировать запланированный пост: /editpost <id> <новый текст>"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Использование:\n"
            "`/editpost <id> <новый текст>`",
            parse_mode='Markdown'
        )
        return
    
    try:
        post_id = int(context.args[0])
        new_content = ' '.join(context.args[1:])
        
        db_pool = get_db_pool()
        async with db_pool.acquire() as conn:
            result = await conn.execute('''
                UPDATE scheduled_posts
                SET content_ru = $1
                WHERE id = $2 AND user_id = $3 AND status = 'pending'
            ''', new_content, post_id, user.id)
        
        if result == "UPDATE 1":
            await update.message.reply_text(f"✅ Пост **#{post_id}** обновлён!", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Пост **#{post_id}** не найден", parse_mode='Markdown')
    
    except ValueError:
        await update.message.reply_text("❌ Неверный ID поста")
    except Exception as e:
        logger.error(f"Ошибка редактирования поста: {e}")
        await update.message.reply_text("❌ Ошибка редактирования")

async def delete_scheduled_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить запланированный пост: /delpost <id>"""
    user = update.effective_user
    await update_user_stats(user.id, user.username, user.first_name)
    
    if not context.args:
        await update.message.reply_text(
            "❌ Использование: `/delpost <id>`",
            parse_mode='Markdown'
        )
        return
    
    try:
        post_id = int(context.args[0])
        
        db_pool = get_db_pool()
        async with db_pool.acquire() as conn:
            result = await conn.execute('''
                DELETE FROM scheduled_posts
                WHERE id = $1 AND user_id = $2 AND status = 'pending'
            ''', post_id, user.id)
        
        if result == "DELETE 1":
            await update.message.reply_text(f"✅ Пост **#{post_id}** удалён!", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Пост **#{post_id}** не найден", parse_mode='Markdown')
    
    except ValueError:
        await update.message.reply_text("❌ Неверный ID поста")
    except Exception as e:
        logger.error(f"Ошибка удаления поста: {e}")
        await update.message.reply_text("❌ Ошибка удаления")
