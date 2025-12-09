import os
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import asyncpg
from contextlib import asynccontextmanager

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Глобальный пул соединений с БД
db_pool = None

# Инициализация базы данных
async def init_db():
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL)
        logger.info("✅ Подключение к базе данных успешно!")
        
        # Создаём таблицы если их нет
        async with db_pool.acquire() as conn:
            # Таблица для заметок
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица для задач
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
            
            # Таблица для статистики использования
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    total_messages INT DEFAULT 0,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
        logger.info("✅ Таблицы созданы/проверены!")
        logger.info("🚀 Бот запущен с PostgreSQL!")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к БД: {e}")

# Обновление статистики пользователя
async def update_user_stats(user_id: int, username: str, first_name: str):
    try:
        async with db_pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO user_stats (user_id, username, first_name, total_messages, last_active)
                VALUES ($1, $2, $3, 1, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    total_messages = user_stats.total_messages + 1,
                    last_active = CURRENT_TIMESTAMP
            ''', user_id, username, first_name)
    except Exception as e:
        logger.error(f"Ошибка обновления статистики: {e}")

# Создаем главное меню
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("💬 Спросить AI"), KeyboardButton("📝 Заметка")],
        [KeyboardButton("✅ Задачи"), KeyboardButton("🎨 Идея для арта")],
        [KeyboardButton("📊 Статистика"), KeyboardButton("ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update_user_stats(user.id, user.username or "", user.first_name or "")
    
    welcome_message = f"""
🎨 Привет, {user.first_name}! 

Я твой AI-помощник для 3D-артистов и креаторов!

✨ Теперь с постоянной базой данных! Все твои заметки и задачи сохраняются навсегда!

Мои возможности:
• 💬 Общение с AI (Google Gemini)
• 📝 Сохранение заметок (в PostgreSQL)
• ✅ Управление задачами с приоритетами
• 🎨 Генерация идей для артов
• 📊 Твоя статистика использования

Выбери действие в меню или просто напиши мне! 🚀
"""
    await update.message.reply_text(welcome_message, reply_markup=get_main_keyboard())

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update_user_stats(user.id, user.username or "", user.first_name or "")
    
    help_text = """
🔧 Доступные команды:

/start - Начать работу с ботом
/help - Показать эту справку
/note <текст> - Сохранить заметку
/notes - Показать все заметки
/delnote <номер> - Удалить заметку
/task <описание> - Добавить задачу
/tasks - Показать все задачи
/complete <номер> - Отметить задачу выполненной
/deltask <номер> - Удалить задачу
/ask <вопрос> - Спросить AI
/stats - Моя статистика

📱 Или используй кнопки меню!

💾 Все данные сохраняются в базе PostgreSQL навсегда!
"""
    await update.message.reply_text(help_text)

# Обработка команды /note
async def add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update_user_stats(user.id, user.username or "", user.first_name or "")
    
    if not context.args:
        await update.message.reply_text("❌ Использование: /note <текст заметки>")
        return
    
    note_text = ' '.join(context.args)
    
    try:
        async with db_pool.acquire() as conn:
            await conn.execute(
                'INSERT INTO notes (user_id, text) VALUES ($1, $2)',
                user.id, note_text
            )
        await update.message.reply_text(f"✅ Заметка сохранена в базу данных!\n📝 {note_text}")
    except Exception as e:
        logger.error(f"Ошибка сохранения заметки: {e}")
        await update.message.reply_text("❌ Ошибка сохранения заметки")

# Показать все заметки
async def show_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update_user_stats(user.id, user.username or "", user.first_name or "")
    
    try:
        async with db_pool.acquire() as conn:
            notes = await conn.fetch(
                'SELECT id, text, created_at FROM notes WHERE user_id = $1 ORDER BY created_at DESC',
                user.id
            )
        
        if not notes:
            await update.message.reply_text("📝 У вас пока нет заметок")
            return
        
        notes_text = f"📝 Ваши заметки ({len(notes)}):\n\n"
        for note in notes:
            date_str = note['created_at'].strftime("%d.%m.%Y %H:%M")
            notes_text += f"#{note['id']} {note['text']}\n📅 {date_str}\n\n"
        
        notes_text += "\n💡 Удалить: /delnote <номер>"
        await update.message.reply_text(notes_text)
    except Exception as e:
        logger.error(f"Ошибка получения заметок: {e}")
        await update.message.reply_text("❌ Ошибка получения заметок")

# Удалить заметку
async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update_user_stats(user.id, user.username or "", user.first_name or "")
    
    if not context.args:
        await update.message.reply_text("❌ Использование: /delnote <номер заметки>")
        return
    
    try:
        note_id = int(context.args[0])
        async with db_pool.acquire() as conn:
            result = await conn.execute(
                'DELETE FROM notes WHERE id = $1 AND user_id = $2',
                note_id, user.id
            )
        
        if result == "DELETE 1":
            await update.message.reply_text(f"✅ Заметка #{note_id} удалена!")
        else:
            await update.message.reply_text(f"❌ Заметка #{note_id} не найдена")
    except ValueError:
        await update.message.reply_text("❌ Неверный номер заметки")
    except Exception as e:
        logger.error(f"Ошибка удаления заметки: {e}")
        await update.message.reply_text("❌ Ошибка удаления заметки")

# Обработка команды /task
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update_user_stats(user.id, user.username or "", user.first_name or "")
    
    if not context.args:
        await update.message.reply_text("❌ Использование: /task <описание задачи>")
        return
    
    task_text = ' '.join(context.args)
    
    try:
        async with db_pool.acquire() as conn:
            await conn.execute(
                'INSERT INTO tasks (user_id, text) VALUES ($1, $2)',
                user.id, task_text
            )
        await update.message.reply_text(f"✅ Задача добавлена!\n📋 {task_text}")
    except Exception as e:
        logger.error(f"Ошибка добавления задачи: {e}")
        await update.message.reply_text("❌ Ошибка добавления задачи")

# Показать все задачи
async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update_user_stats(user.id, user.username or "", user.first_name or "")
    
    try:
        async with db_pool.acquire() as conn:
            tasks = await conn.fetch(
                'SELECT id, text, completed, created_at FROM tasks WHERE user_id = $1 ORDER BY completed, created_at DESC',
                user.id
            )
        
        if not tasks:
            await update.message.reply_text("📋 У вас пока нет задач")
            return
        
        active_tasks = [t for t in tasks if not t['completed']]
        completed_tasks = [t for t in tasks if t['completed']]
        
        tasks_text = f"📋 Ваши задачи:\n\n"
        
        if active_tasks:
            tasks_text += "⏳ Активные:\n"
            for task in active_tasks:
                date_str = task['created_at'].strftime("%d.%m.%Y")
                tasks_text += f"#{task['id']} {task['text']}\n📅 {date_str}\n\n"
        
        if completed_tasks:
            tasks_text += "✅ Выполненные:\n"
            for task in completed_tasks:
                tasks_text += f"#{task['id']} ~~{task['text']}~~\n\n"
        
        tasks_text += "\n💡 Команды:\n/complete <номер> - отметить выполненной\n/deltask <номер> - удалить"
        await update.message.reply_text(tasks_text)
    except Exception as e:
        logger.error(f"Ошибка получения задач: {e}")
        await update.message.reply_text("❌ Ошибка получения задач")

# Отметить задачу выполненной
async def complete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update_user_stats(user.id, user.username or "", user.first_name or "")
    
    if not context.args:
        await update.message.reply_text("❌ Использование: /complete <номер задачи>")
        return
    
    try:
        task_id = int(context.args[0])
        async with db_pool.acquire() as conn:
            result = await conn.execute(
                'UPDATE tasks SET completed = TRUE WHERE id = $1 AND user_id = $2',
                task_id, user.id
            )
        
        if result == "UPDATE 1":
            await update.message.reply_text(f"✅ Задача #{task_id} выполнена! Молодец! 🎉")
        else:
            await update.message.reply_text(f"❌ Задача #{task_id} не найдена")
    except ValueError:
        await update.message.reply_text("❌ Неверный номер задачи")
    except Exception as e:
        logger.error(f"Ошибка обновления задачи: {e}")
        await update.message.reply_text("❌ Ошибка обновления задачи")

# Удалить задачу
async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update_user_stats(user.id, user.username or "", user.first_name or "")
    
    if not context.args:
        await update.message.reply_text("❌ Использование: /deltask <номер задачи>")
        return
    
    try:
        task_id = int(context.args[0])
        async with db_pool.acquire() as conn:
            result = await conn.execute(
                'DELETE FROM tasks WHERE id = $1 AND user_id = $2',
                task_id, user.id
            )
        
        if result == "DELETE 1":
            await update.message.reply_text(f"✅ Задача #{task_id} удалена!")
        else:
            await update.message.reply_text(f"❌ Задача #{task_id} не найдена")
    except ValueError:
        await update.message.reply_text("❌ Неверный номер задачи")
    except Exception as e:
        logger.error(f"Ошибка удаления задачи: {e}")
        await update.message.reply_text("❌ Ошибка удаления задачи")

# Показать статистику
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update_user_stats(user.id, user.username or "", user.first_name or "")
    
    try:
        async with db_pool.acquire() as conn:
            # Получаем статистику пользователя
            stats = await conn.fetchrow(
                'SELECT total_messages, last_active FROM user_stats WHERE user_id = $1',
                user.id
            )
            
            # Считаем заметки и задачи
            notes_count = await conn.fetchval(
                'SELECT COUNT(*) FROM notes WHERE user_id = $1',
                user.id
            )
            
            tasks_total = await conn.fetchval(
                'SELECT COUNT(*) FROM tasks WHERE user_id = $1',
                user.id
            )
            
            tasks_completed = await conn.fetchval(
                'SELECT COUNT(*) FROM tasks WHERE user_id = $1 AND completed = TRUE',
                user.id
            )
            
            tasks_active = tasks_total - tasks_completed
        
        stats_text = f"""
📊 Твоя статистика:

👤 Пользователь: {user.first_name}
💬 Всего сообщений: {stats['total_messages']}
📝 Заметок сохранено: {notes_count}
📋 Задач всего: {tasks_total}
   ⏳ Активных: {tasks_active}
   ✅ Выполнено: {tasks_completed}

⏰ Последняя активность: {stats['last_active'].strftime("%d.%m.%Y %H:%M")}

Продолжай в том же духе! 🚀
"""
        await update.message.reply_text(stats_text)
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        await update.message.reply_text("❌ Ошибка получения статистики")

# Обработка команды /ask - вопрос к AI
async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update_user_stats(user.id, user.username or "", user.first_name or "")
    
    if not context.args:
        await update.message.reply_text("❌ Использование: /ask <ваш вопрос>")
        return
    
    question = ' '.join(context.args)
    await update.message.reply_text("🤔 Думаю...")
    
    try:
        response = model.generate_content(question)
        await update.message.reply_text(f"🤖 {response.text}")
    except Exception as e:
        logger.error(f"Ошибка Gemini API: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обращении к AI. Попробуйте позже.")

# Обработка текстовых сообщений (кнопки меню)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update_user_stats(user.id, user.username or "", user.first_name or "")
    
    text = update.message.text
    
    if text == "💬 Спросить AI":
        await update.message.reply_text("Задайте ваш вопрос AI, используя команду:\n/ask <ваш вопрос>\n\nИли просто напишите свой вопрос!")
    
    elif text == "📝 Заметка":
        await update.message.reply_text("Чтобы добавить заметку:\n/note <текст заметки>\n\nПосмотреть заметки:\n/notes\n\nУдалить:\n/delnote <номер>")
    
    elif text == "✅ Задачи":
        await update.message.reply_text("📋 Управление задачами:\n\n/task <описание> - добавить\n/tasks - показать все\n/complete <номер> - выполнить\n/deltask <номер> - удалить")
    
    elif text == "🎨 Идея для арта":
        await update.message.reply_text("🤔 Генерирую идею...")
        try:
            prompt = "Предложи креативную и детальную идею для 3D-арта или визуализации. Опиши концепт вдохновляюще на русском языке, включая стиль, настроение, цветовую палитру и технические детали."
            response = model.generate_content(prompt)
            await update.message.reply_text(f"💡 {response.text}")
        except Exception as e:
            logger.error(f"Ошибка Gemini API: {e}")
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
    
    elif text == "📊 Статистика":
        await show_stats(update, context)
    
    elif text == "ℹ️ Помощь":
        await help_command(update, context)
    
    else:
        # Любой другой текст отправляем в AI
        await update.message.reply_text("🤔 Обрабатываю...")
        try:
            response = model.generate_content(text)
            await update.message.reply_text(f"🤖 {response.text}")
        except Exception as e:
            logger.error(f"Ошибка Gemini API: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обращении к AI.")

# Обработка ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

async def post_init(application: Application):
    """Вызывается после инициализации приложения"""
    await init_db()

def main():
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("note", add_note))
    application.add_handler(CommandHandler("notes", show_notes))
    application.add_handler(CommandHandler("delnote", delete_note))
    application.add_handler(CommandHandler("task", add_task))
    application.add_handler(CommandHandler("tasks", show_tasks))
    application.add_handler(CommandHandler("complete", complete_task))
    application.add_handler(CommandHandler("deltask", delete_task))
    application.add_handler(CommandHandler("ask", ask_ai))
    application.add_handler(CommandHandler("stats", show_stats))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("🤖 Запуск бота...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
