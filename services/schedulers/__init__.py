"""
Планировщики автоматических задач
"""

from .notifications import start_notification_scheduler
from .trends import start_trends_scheduler
from .auto_posting import start_autoposting_scheduler

__all__ = [
    'start_notification_scheduler',
    'start_trends_scheduler',
    'start_autoposting_scheduler',
]
