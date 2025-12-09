"""


Обработчики настроек уведомлений


"""





import logging


from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton


from telegram.ext import ContextTypes


from database.db import get_db_pool, update_user_stats





logger = logging.getLogger(__name__)





async def notification_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):


    """Показать настройки уведомлений: /notifications"""


    user = update.effective_user


    await update_user_stats(user.id, user.username, user.first_name)


    


    db_pool = get_db_pool()


    if not db_pool:


        await update.message.reply_text("❌ База данных недоступна.")


        return


    


    try:


        async with db_pool.acquire() as conn:


            # Получаем или создаем настройки


            settings = await conn.fetchrow(


                'SELECT * FROM notification_settings WHERE user_id = $1',


                user.id


            )


            


            if not settings:


                await conn.execute(


                    'INSERT INTO notification_settings (user_id) VALUES ($1)',


                    user.id


                )


                settings = await conn.fetchrow(


                    'SELECT * FROM notification_settings WHERE user_id = $1',


                    user.id


                )


        


        def status_emoji(enabled):


            return "✅" if enabled else "❌"


        


        message = "⏰ **Настройки уведомлений**\n\n"


        message += f"{status_emoji(settings['motivation'])} **08:00** — Мотивация дня + арт\n"


        message += f"{status_emoji(settings['idea'])} **09:00** — Идея для проекта\n"


        message += f"{status_emoji(settings['trends'])} **10:00** — Тренды + музыка\n"


        message += f"{status_emoji(settings['jobs'])} **11:00** — Вакансии и фриланс\n"


        message += f"{status_emoji(settings['assets'])} **12:00** — Топ ассетов\n"


        message += f"{status_emoji(settings['reminders'])} **Каждые 2 часа** — Напоминания\n\n"


        


        message += "💡 **Переключить:**\n"


        message += "`/togglenotif motivation` — мотивация\n"


        message += "`/togglenotif idea` — идеи\n"


        message += "`/togglenotif trends` — тренды\n"


        message += "`/togglenotif jobs` — вакансии\n"


        message += "`/togglenotif assets` — ассеты\n"


        message += "`/togglenotif reminders` — напоминания"


        


        await update.message.reply_text(message, parse_mode='Markdown')


        


    except Exception as e:


        logger.error(f"Ошибка получения настроек: {e}")


        await update.message.reply_text("❌ Ошибка получения настроек")





async def toggle_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):


    """Переключить уведомление: /togglenotif <тип>"""


    user = update.effective_user


    await update_user_stats(user.id, user.username, user.first_name)


    


    if not context.args:


        await update.message.reply_text(


            "❌ Использование: `/togglenotif <тип>`\n\n"


            "Типы: motivation, idea, trends, jobs, assets, reminders",


            parse_mode='Markdown'


        )


        return


    


    notif_type = context.args[0].lower()


    valid_types = ['motivation', 'idea', 'trends', 'jobs', 'assets', 'reminders']


    


    if notif_type not in valid_types:


        await update.message.reply_text(


            f"❌ Неверный тип уведомления: {notif_type}\n\n"


            f"Доступные: {', '.join(valid_types)}",


            parse_mode='Markdown'


        )


        return


    


    db_pool = get_db_pool()


    if not db_pool:


        await update.message.reply_text("❌ База данных недоступна.")


        return


    


    try:


        async with db_pool.acquire() as conn:


            # Переключаем состояние


            query = f"UPDATE notification_settings SET {notif_type} = NOT {notif_type} WHERE user_id = $1 RETURNING {notif_type}"


            new_state = await conn.fetchval(query, user.id)


        


        status = "включены ✅" if new_state else "выключены ❌"


        


        notif_names = {


            'motivation': 'Мотивация дня',


            'idea': 'Идеи для проектов',


            'trends': 'Тренды',


            'jobs': 'Вакансии',


            'assets': 'Топ ассетов',


            'reminders': 'Напоминания',


        }


        


        await update.message.reply_text(


            f"✅ **{notif_names[notif_type]}** {status}\n\n"


            f"Все настройки: /notifications",


            parse_mode='Markdown'


        )


        


    except Exception as e:


        logger.error(f"Ошибка переключения уведомления: {e}")


        await update.message.reply_text("❌ Ошибка изменения настроек")
