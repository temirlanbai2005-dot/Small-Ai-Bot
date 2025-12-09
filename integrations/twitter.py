"""
Интеграция с X (Twitter) API v2
"""

import logging
import tweepy
from config.settings import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_SECRET,
    TWITTER_BEARER_TOKEN
)

logger = logging.getLogger(__name__)

# Инициализация клиента Twitter API v2
def get_twitter_client():
    """Создание клиента Twitter API"""
    try:
        client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET,
            wait_on_rate_limit=True
        )
        return client
    except Exception as e:
        logger.error(f"Ошибка создания Twitter клиента: {e}")
        return None

async def post_to_twitter(text: str, image_path: str = None) -> dict:
    """
    Публикация твита
    
    Args:
        text: Текст твита (максимум 280 символов)
        image_path: Путь к изображению (опционально)
    
    Returns:
        dict: {'success': bool, 'url': str, 'tweet_id': str}
    """
    if not TWITTER_API_KEY or not TWITTER_ACCESS_TOKEN:
        logger.error("Twitter API ключи не настроены")
        return {'success': False, 'error': 'API keys not configured'}
    
    try:
        client = get_twitter_client()
        if not client:
            return {'success': False, 'error': 'Failed to create client'}
        
        # Обрезаем текст если слишком длинный
        if len(text) > 280:
            text = text[:277] + '...'
            logger.warning(f"Твит обрезан до 280 символов")
        
        # Публикуем твит
        if image_path:
            # API v1.1 для загрузки медиа
            auth = tweepy.OAuth1UserHandler(
                TWITTER_API_KEY,
                TWITTER_API_SECRET,
                TWITTER_ACCESS_TOKEN,
                TWITTER_ACCESS_SECRET
            )
            api = tweepy.API(auth)
            
            # Загружаем изображение
            media = api.media_upload(image_path)
            
            # Публикуем с изображением
            response = client.create_tweet(text=text, media_ids=[media.media_id])
        else:
            response = client.create_tweet(text=text)
        
        tweet_id = response.data['id']
        tweet_url = f"https://twitter.com/user/status/{tweet_id}"
        
        logger.info(f"✅ Твит опубликован: {tweet_url}")
        
        return {
            'success': True,
            'url': tweet_url,
            'tweet_id': str(tweet_id)
        }
    
    except tweepy.TweepyException as e:
        logger.error(f"Ошибка публикации в Twitter: {e}")
        return {'success': False, 'error': str(e)}
    
    except Exception as e:
        logger.error(f"Неожиданная ошибка Twitter: {e}")
        return {'success': False, 'error': str(e)}

async def delete_tweet(tweet_id: str) -> bool:
    """Удаление твита"""
    try:
        client = get_twitter_client()
        if not client:
            return False
        
        client.delete_tweet(tweet_id)
        logger.info(f"✅ Твит {tweet_id} удален")
        return True
    
    except Exception as e:
        logger.error(f"Ошибка удаления твита: {e}")
        return False

async def check_twitter_auth() -> bool:
    """Проверка авторизации Twitter"""
    try:
        client = get_twitter_client()
        if not client:
            return False
        
        # Проверяем получение данных о текущем пользователе
        me = client.get_me()
        if me.data:
            logger.info(f"✅ Twitter авторизован: @{me.data.username}")
            return True
        return False
    
    except Exception as e:
        logger.error(f"Ошибка проверки Twitter авторизации: {e}")
        return False

async def get_tweet_analytics(tweet_id: str) -> dict:
    """Получение аналитики твита"""
    try:
        client = get_twitter_client()
        if not client:
            return {}
        
        tweet = client.get_tweet(
            tweet_id,
            tweet_fields=['public_metrics']
        )
        
        if tweet.data:
            metrics = tweet.data.public_metrics
            return {
                'likes': metrics.get('like_count', 0),
                'retweets': metrics.get('retweet_count', 0),
                'replies': metrics.get('reply_count', 0),
                'impressions': metrics.get('impression_count', 0),
            }
        
        return {}
    
    except Exception as e:
        logger.error(f"Ошибка получения аналитики: {e}")
        return {}
