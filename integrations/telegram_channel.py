"""
Интеграция с Telegram каналами
"""

import logging
from telegram import Bot
from telegram.error import TelegramError
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID

logger = logging.getLogger(__name__)

async def post_to_telegram_channel(text: str, image_path: str = None, channel_id: str = None) -> dict:
    """
    Публикация в Telegram канал
    
    Args:
        text: Текст сообщения (Markdown поддерживается)
        image_path: Путь к изображению (опционально)
        channel_id: ID канала (по умолчанию из настроек)
    
    Returns:
        dict: {'success': bool, 'url': str, 'message_id': int}
    """
    if not TELEGRAM_TOKEN:
        logger.error("Telegram токен не настроен")
        return {'success': False, 'error': 'Token not configured'}
    
    channel = channel_id or TELEGRAM_CHANNEL_ID
    
    if not channel:
        logger.error("Telegram канал не указан")
        return {'success': False, 'error': 'Channel not specified'}
    
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        
        # Публикуем сообщение
        if image_path:
            # С изображением
            with open(image_path, 'rb') as photo:
                message = await bot.send_photo(
                    chat_id=channel,
                    photo=photo,
                    caption=text,
                    parse_mode='Markdown'
                )
        else:
            # Только текст
            message = await bot.send_message(
                chat_id=channel,
                text=text,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
        
        # Формируем URL поста
        channel_username = channel.replace('@', '')
        post_url = f"https://t.me/{channel_username}/{message.message_id}"
        
        logger.info(f"✅ Пост опубликован в Telegram: {post_url}")
        
        return {
            'success': True,
            'url': post_url,
            'message_id': message.message_id
        }
    
    except TelegramError as e:
        logger.error(f"Ошибка публикации в Telegram: {e}")
        return {'success': False, 'error': str(e)}
    
    except Exception as e:
        logger.error(f"Неожиданная ошибка Telegram: {e}")
        return {'success': False, 'error': str(e)}

async def post_to_telegram(text: str, image_path: str = None) -> dict:
    """Alias для post_to_telegram_channel"""
    return await post_to_telegram_channel(text, image_path)

async def edit_telegram_post(channel_id: str, message_id: int, new_text: str) -> bool:
    """Редактирование поста в канале"""
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        
        await bot.edit_message_text(
            chat_id=channel_id,
            message_id=message_id,
            text=new_text,
            parse_mode='Markdown'
        )
        
        logger.info(f"✅ Пост {message_id} отредактирован")
        return True
    
    except Exception as e:
        logger.error(f"Ошибка редактирования поста: {e}")
        return False

async def delete_telegram_post(channel_id: str, message_id: int) -> bool:
    """Удаление поста из канала"""
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        
        await bot.delete_message(
            chat_id=channel_id,
            message_id=message_id
        )
        
        logger.info(f"✅ Пост {message_id} удален")
        return True
    
    except Exception as e:
        logger.error(f"Ошибка удаления поста: {e}")
        return False

async def get_telegram_post_views(channel_id: str, message_id: int) -> int:
    """Получение количества просмотров поста"""
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        
        # Telegram Bot API не предоставляет просмотры напрямую
        # Это ограничение API
        logger.warning("Получение просмотров недоступно через Bot API")
        return 0
    
    except Exception as e:
        logger.error(f"Ошибка получения просмотров: {e}")
        return 0
