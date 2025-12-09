"""
Обработчики команд Telegram бота
"""

from .basic import start, help_command
from .notes import add_note, show_notes, delete_note
from .tasks import add_task, show_tasks, complete_task, delete_task
from .ai import ask_ai
from .stats import show_stats
from .trends import show_trends, toggle_trends_notifications
from .content_plan import create_content_plan, schedule_post, view_scheduled_posts, edit_scheduled_post, delete_scheduled_post
from .notifications import notification_settings, toggle_notification
from .messages import handle_message

__all__ = [
    'start',
    'help_command',
    'add_note',
    'show_notes',
    'delete_note',
    'add_task',
    'show_tasks',
    'complete_task',
    'delete_task',
    'ask_ai',
    'show_stats',
    'show_trends',
    'toggle_trends_notifications',
    'create_content_plan',
    'schedule_post',
    'view_scheduled_posts',
    'edit_scheduled_post',
    'delete_scheduled_post',
    'notification_settings',
    'toggle_notification',
    'handle_message',
]
