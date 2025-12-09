"""
SQL-схемы и модели данных
"""

# Перечисления для статусов

POST_STATUSES = {
    'PENDING': 'pending',      # Ожидает публикации
    'POSTED': 'posted',        # Опубликован
    'FAILED': 'failed',        # Ошибка
    'CANCELLED': 'cancelled',  # Отменён
}

TASK_PRIORITIES = {
    'LOW': 'low',
    'MEDIUM': 'medium',
    'HIGH': 'high',
    'URGENT': 'urgent',
}

TREND_TYPES = {
    'ARTSTATION': 'artstation',
    'MUSIC': 'music',
    'JOBS': 'jobs',
    'ASSETS': 'assets',
}

# SQL-запросы для частого использования

QUERIES = {
    # Заметки
    'get_user_notes': '''
        SELECT id, text, created_at 
        FROM notes 
        WHERE user_id = $1 
        ORDER BY created_at DESC
    ''',
    
    'add_note': '''
        INSERT INTO notes (user_id, text) 
        VALUES ($1, $2) 
        RETURNING id
    ''',
    
    'delete_note': '''
        DELETE FROM notes 
        WHERE id = $1 AND user_id = $2
    ''',
    
    # Задачи
    'get_user_tasks': '''
        SELECT id, text, priority, deadline, completed, created_at 
        FROM tasks 
        WHERE user_id = $1 
        ORDER BY completed, priority DESC, created_at DESC
    ''',
    
    'add_task': '''
        INSERT INTO tasks (user_id, text, priority, deadline) 
        VALUES ($1, $2, $3, $4) 
        RETURNING id
    ''',
    
    'complete_task': '''
        UPDATE tasks 
        SET completed = TRUE 
        WHERE id = $1 AND user_id = $2
    ''',
    
    'delete_task': '''
        DELETE FROM tasks 
        WHERE id = $1 AND user_id = $2
    ''',
    
    # Запланированные посты
    'get_scheduled_posts': '''
        SELECT id, platform, content_ru, scheduled_time, status 
        FROM scheduled_posts 
        WHERE user_id = $1 AND status = 'pending'
        ORDER BY scheduled_time ASC
    ''',
    
    'add_scheduled_post': '''
        INSERT INTO scheduled_posts (user_id, platform, content_ru, content_en, scheduled_time) 
        VALUES ($1, $2, $3, $4, $5) 
        RETURNING id
    ''',
    
    'update_post_status': '''
        UPDATE scheduled_posts 
        SET status = $1, posted_at = CURRENT_TIMESTAMP, error_message = $2 
        WHERE id = $3
    ''',
    
    # Настройки уведомлений
    'get_notification_settings': '''
        SELECT * FROM notification_settings WHERE user_id = $1
    ''',
    
    'init_notification_settings': '''
        INSERT INTO notification_settings (user_id) 
        VALUES ($1) 
        ON CONFLICT (user_id) DO NOTHING
    ''',
    
    'toggle_notification': '''
        UPDATE notification_settings 
        SET {column} = NOT {column} 
        WHERE user_id = $1
    ''',
    
    # Статистика
    'get_user_stats': '''
        SELECT total_messages, last_active, created_at 
        FROM user_stats 
        WHERE user_id = $1
    ''',
}
