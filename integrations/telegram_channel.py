"""
Интеграция с Telegram каналами
"""

import os
import logging
from telegram import Bot

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', '')

def is_telegram_channel_configured():
    """Проверка настроен ли канал"""
    return bool(TELEGRAM_CHANNEL_ID)

async def post_to_telegram_channel(text: str, image_path: str = None, channel_id: str = None) -> dict:
    """Публикация в Telegram канал"""
    
    channel = channel_id or TELEGRAM_CHANNEL_ID
    
    if not channel:
        logger.warning("⚠️ Telegram канал не настроен")
        return {'success': False, 'error': 'Channel not configured'}
    
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        
        if image_path:
            with open(image_path, 'rb') as photo:
                message = await bot.send_photo(
                    chat_id=channel,
                    photo=photo,
                    caption=text,
                    parse_mode='Markdown'
                )
        else:
            message = await bot.send_message(
                chat_id=channel,
                text=text,
                parse_mode='Markdown'
            )
        
        channel_username = channel.replace('@', '')
        post_url = f"https://t.me/{channel_username}/{message.message_id}"
        
        logger.info(f"✅ Пост в Telegram: {post_url}")
        return {'success': True, 'url': post_url, 'message_id': message.message_id}
    
    except Exception as e:
        logger.error(f"❌ Ошибка Telegram: {e}")
        return {'success': False, 'error': str(e)}
