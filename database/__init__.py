"""
Модуль для работы с базой данных
"""

from .db import init_db, close_db, get_db_pool, update_user_stats
from .models import *

__all__ = [
    'init_db',
    'close_db',
    'get_db_pool',
    'update_user_stats',
]
