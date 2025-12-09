"""
Планировщик автоматического постинга в соцсети
"""

import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application

from config.settings import TIMEZONE
from database.db import get_db_pool

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone=TIMEZONE)

async def check_scheduled_posts(bot):
    """Проверка и публикация запланированных постов"""
    logger.info("🔍 Проверка запланированных постов...")
    
    db_pool = get_db_pool()
    if not db_pool:
        return
    
    try:
        async with db_pool.acquire() as conn:
            # Получаем посты, которые нужно опубликовать
            now = datetime.now()
            posts = await conn.fetch('''
                SELECT id, user_id, platform, content_en, content_ru, scheduled_time
                FROM scheduled_posts
                WHERE status = 'pending'
                AND scheduled_time <= $1
                ORDER BY scheduled_time ASC
                LIMIT 10
            ''', now)
        
        if not posts:
            logger.info("Нет постов для публикации")
            return
        
        logger.info(f"Найдено {len(posts)} постов для публикации")
        
        for post in posts:
            try:
                await publish_post(post, bot)
            except Exception as e:
                logger.error(f"Ошибка публикации поста #{post['id']}: {e}")
                
                # Отмечаем как failed
                async with db_pool.acquire() as conn:
                    await conn.execute('''
                        UPDATE scheduled_posts
                        SET status = 'failed', error_message = $1
                        WHERE id = $2
                    ''', str(e), post['id'])
    
    except Exception as e:
        logger.error(f"Ошибка проверки постов: {e}")

async def publish_post(post: dict, bot):
    """Публикация конкретного поста"""
    platform = post['platform']
    content = post['content_en'] or post['content_ru']
    
    logger.info(f"📤 Публикация поста #{post['id']} в {platform}...")
    
    # Импортируем интеграции динамически
    from integrations.twitter import post_to_twitter
    from integrations.telegram_channel import post_to_telegram
    from integrations.linkedin import post_to_linkedin
    # ... другие интеграции
    
    result = None
    
    try:
        if platform == 'X (Twitter)':
            result = await post_to_twitter(content)
        
        elif platform == 'Telegram':
            result = await post_to_telegram(content)
        
        elif platform == 'LinkedIn':
            result = await post_to_linkedin(content)
        
        # ... другие платформы
        
        else:
            logger.warning(f"Автопостинг в {platform} пока не поддерживается")
            return
        
        # Отмечаем как опубликованный
        db_pool = get_db_pool()
        async with db_pool.acquire() as conn:
            await conn.execute('''
                UPDATE scheduled_posts
                SET status = 'posted', posted_at = CURRENT_TIMESTAMP
                WHERE id = $1
            ''', post['id'])
            
            # Сохраняем в историю
            await conn.execute('''
                INSERT INTO post_history (user_id, platform, content, post_url)
                VALUES ($1, $2, $3, $4)
            ''', post['user_id'], platform, content, result.get('url') if result else None)
        
        # Уведомляем пользователя
        try:
            await bot.send_message(
                chat_id=post['user_id'],
                text=f"✅ Пост успешно опубликован в **{platform}**!\n\n{content[:100]}...",
                parse_mode='Markdown'
            )
        except:
            pass
        
        logger.info(f"✅ Пост #{post['id']} опубликован в {platform}")
    
    except Exception as e:
        logger.error(f"Ошибка публикации в {platform}: {e}")
        raise

async def start_autoposting_scheduler(application: Application):
    """Запуск планировщика автопостинга"""
    bot = application.bot
    
    # Проверяем каждые 5 минут
    scheduler.add_job(
        check_scheduled_posts,
        CronTrigger(minute='*/5', timezone=TIMEZONE),
        args=[bot],
        id='check_posts'
    )
    
    scheduler.start()
    logger.info("✅ Планировщик автопостинга запущен")
