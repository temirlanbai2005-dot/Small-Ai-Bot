"""
Клавиатуры для Telegram бота
"""

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config.platforms import SUPPORTED_PLATFORMS

def get_main_keyboard():
    """Главное меню бота"""
    keyboard = [
        [KeyboardButton("💬 Спросить AI"), KeyboardButton("📝 Заметка")],
        [KeyboardButton("✅ Задачи"), KeyboardButton("🎨 Идея для арта")],
        [KeyboardButton("🔥 Тренды"), KeyboardButton("📅 Контент-план")],
        [KeyboardButton("⏰ Уведомления"), KeyboardButton("📊 Статистика")],
        [KeyboardButton("ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_platform_keyboard():
    """Клавиатура выбора платформы"""
    keyboard = []
    row = []
    
    platform_emojis = {
        'Instagram': '📷',
        'TikTok': '🎵',
        'X (Twitter)': '🐦',
        'YouTube': '▶️',
        'LinkedIn': '💼',
        'Pinterest': '📌',
        'Threads': '🧵',
        'Telegram': '✈️',
        'ArtStation': '🎨',
    }
    
    for i, platform in enumerate(SUPPORTED_PLATFORMS):
        emoji = platform_emojis.get(platform, '📱')
        row.append(KeyboardButton(f"{emoji} {platform}"))
        
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([KeyboardButton("« Назад в меню")])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_notification_keyboard():
    """Клавиатура настройки уведомлений"""
    keyboard = [
        [
            InlineKeyboardButton("🌅 Мотивация", callback_data="toggle_motivation"),
            InlineKeyboardButton("💡 Идеи", callback_data="toggle_idea")
        ],
        [
            InlineKeyboardButton("🔥 Тренды", callback_data="toggle_trends"),
            InlineKeyboardButton("💼 Вакансии", callback_data="toggle_jobs")
        ],
        [
            InlineKeyboardButton("🎨 Ассеты", callback_data="toggle_assets"),
            InlineKeyboardButton("⏰ Напоминания", callback_data="toggle_reminders")
        ],
        [
            InlineKeyboardButton("✅ Готово", callback_data="notif_done")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_keyboard(action_id: str):
    """Клавиатура подтверждения действия"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data=f"confirm_{action_id}"),
            InlineKeyboardButton("❌ Нет", callback_data=f"cancel_{action_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_post_actions_keyboard(post_id: int):
    """Клавиатура действий с постом"""
    keyboard = [
        [
            InlineKeyboardButton("✏️ Редактировать", callback_data=f"edit_post_{post_id}"),
            InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_post_{post_id}")
        ],
        [
            InlineKeyboardButton("📤 Опубликовать сейчас", callback_data=f"publish_now_{post_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
