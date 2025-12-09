"""
Интеграции с социальными сетями для автопостинга
"""

from .twitter import post_to_twitter, check_twitter_auth
from .telegram_channel import post_to_telegram, post_to_telegram_channel
from .youtube import post_to_youtube_community
from .pinterest import post_to_pinterest
from .linkedin import post_to_linkedin
from .instagram import post_to_instagram, post_to_threads
from .tiktok import post_to_tiktok

__all__ = [
    'post_to_twitter',
    'check_twitter_auth',
    'post_to_telegram',
    'post_to_telegram_channel',
    'post_to_youtube_community',
    'post_to_pinterest',
    'post_to_linkedin',
    'post_to_instagram',
    'post_to_threads',
    'post_to_tiktok',
]
