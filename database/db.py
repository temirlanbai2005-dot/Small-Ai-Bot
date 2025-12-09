"""
Управление подключением к базе данных PostgreSQL
"""

import os
import asyncpg
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')

# Глобальный пул соединений
db_pool = None

async def init_db():
    """Инициализация базы данных"""
    global db_pool
    
    if not DATABASE_URL:
        logger.error("❌ DATABASE_URL не установлен!")
        return
    
    try:
        logger.info(f"🔄 Подключение к БД...")
        
        # Создание пула соединений
        db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=5,
            command_timeout=60,
            timeout=30
        )
        
        logger.info("✅ Пул соединений создан!")
        
        # Создание таблиц
        async with db_pool.acquire() as conn:
            await _create_tables(conn)
        
        logger.info("✅ Таблицы созданы/проверены!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к БД: {e}")
        db_pool = None
        raise

async def close_db():
    """Закрытие пула соединений"""
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("✅ Соединение с БД закрыто")

def get_db_pool():
    """Получить пул соединений"""
    return db_pool

async def _create_tables(conn):
    """Создание таблиц"""
    
    # Заметки
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Задачи
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            text TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            deadline TIMESTAMP,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Статистика пользователей
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            total_messages INT DEFAULT 0,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Запланированные посты
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            platform TEXT NOT NULL,
            content_ru TEXT NOT NULL,
            content_en TEXT,
            scheduled_time TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'pending',
            posted_at TIMESTAMP,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Настройки уведомлений
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS notification_settings (
            user_id BIGINT PRIMARY KEY,
            motivation BOOLEAN DEFAULT TRUE,
            idea BOOLEAN DEFAULT TRUE,
            trends BOOLEAN DEFAULT TRUE,
            jobs BOOLEAN DEFAULT TRUE,
            assets BOOLEAN DEFAULT TRUE,
            reminders BOOLEAN DEFAULT TRUE,
            timezone TEXT DEFAULT 'Europe/Moscow',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Кэш трендов
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS trends_cache (
            id SERIAL PRIMARY KEY,
            trend_type TEXT NOT NULL,
            data JSONB NOT NULL,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # История постов
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS post_history (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            platform TEXT NOT NULL,
            content TEXT NOT NULL,
            post_url TEXT,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Токены соцсетей
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS platform_tokens (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            platform TEXT NOT NULL,
            access_token TEXT,
            refresh_token TEXT,
            extra_data JSONB,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, platform)
        )
    ''')
    
    # Индексы
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_notes_user ON notes(user_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_user ON tasks(user_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_scheduled_user ON scheduled_posts(user_id)')

async def update_user_stats(user_id: int, username: str = None, first_name: str = None):
    """Обновление статистики пользователя"""
    if not db_pool:
        logger.warning("⚠️ БД не инициализирована")
        return
    
    try:
        async with db_pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO user_stats (user_id, username, first_name, total_messages, last_active)
                VALUES ($1, $2, $3, 1, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id)
                DO UPDATE SET
                    total_messages = user_stats.total_messages + 1,
                    last_active = CURRENT_TIMESTAMP,
                    username = COALESCE($2, user_stats.username),
                    first_name = COALESCE($3, user_stats.first_name)
            ''', user_id, username, first_name)
    except Exception as e:
        logger.error(f"Ошибка обновления статистики: {e}")
