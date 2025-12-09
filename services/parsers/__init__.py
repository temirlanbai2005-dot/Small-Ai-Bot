"""
Парсеры для получения трендов
"""

from .artstation import get_artstation_trends
from .music_trends import get_music_trends, get_tiktok_trends, get_billboard_trends

__all__ = [
    'get_artstation_trends',
    'get_music_trends',
    'get_tiktok_trends',
    'get_billboard_trends',
]
