"""
Интеграция с X (Twitter)
"""

import os
import logging

logger = logging.getLogger(__name__)

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET', '')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')

def is_twitter_configured():
    """Проверка настроен ли Twitter"""
    return bool(TWITTER_API_KEY and TWITTER_ACCESS_TOKEN)

async def post_to_twitter(text: str, image_path: str = None) -> dict:
    """Публикация твита"""
    
    if not is_twitter_configured():
        logger.warning("⚠️ Twitter API не настроен")
        return {'success': False, 'error': 'Twitter API not configured'}
    
    try:
        import tweepy
        
        client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET
        )
        
        # Обрезаем если слишком длинный
        if len(text) > 280:
            text = text[:277] + '...'
        
        # Публикуем
        if image_path:
            # Для изображений нужен API v1.1
            auth = tweepy.OAuth1UserHandler(
                TWITTER_API_KEY,
                TWITTER_API_SECRET,
                TWITTER_ACCESS_TOKEN,
                TWITTER_ACCESS_SECRET
            )
            api = tweepy.API(auth)
            media = api.media_upload(image_path)
            response = client.create_tweet(text=text, media_ids=[media.media_id])
        else:
            response = client.create_tweet(text=text)
        
        tweet_id = response.data['id']
        tweet_url = f"https://twitter.com/user/status/{tweet_id}"
        
        logger.info(f"✅ Твит опубликован: {tweet_url}")
        return {'success': True, 'url': tweet_url, 'tweet_id': str(tweet_id)}
    
    except Exception as e:
        logger.error(f"❌ Ошибка Twitter: {e}")
        return {'success': False, 'error': str(e)}
