import os
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Создаем главное меню
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("💬 Спросить AI"), KeyboardButton("📝 Заметка")],
        [KeyboardButton("✅ Задачи"), KeyboardButton("🎨 Идея для арта")],
        [KeyboardButton("ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_message = f"""
🎨 Привет, {user_name}! 

Я твой AI-помощник для 3D-артистов и креаторов!

Пока я умею:
• 💬 Общаться с помощью AI (Google Gemini)
• 📝 Сохранять заметки
• ✅ Управлять задачами
• 🎨 Генерировать идеи для артов

Выбери действие в меню ниже или просто напиши мне что-нибудь!
"""
    await update.message.reply_text(welcome_message, reply_markup=get_main_keyboard())

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🔧 Доступные команды:

/start - Начать работу с ботом
/help - Показать эту справку
/note <текст> - Сохранить заметку
/notes - Показать все заметки
/task <описание> - Добавить задачу
/tasks - Показать все задачи
/ask <вопрос> - Спросить AI

📱 Или используй кнопки меню!
"""
    await update.message.reply_text(help_text)

# Обработка команды /note
async def add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Использование: /note <текст заметки>")
        return
    
    note_text = ' '.join(context.args)
    user_id = update.effective_user.id
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # Сохраняем в контексте пользователя (временно, позже добавим БД)
    if 'notes' not in context.user_data:
        context.user_data['notes'] = []
    
    context.user_data['notes'].append({
        'text': note_text,
        'date': timestamp
    })
    
    await update.message.reply_text(f"✅ Заметка сохранена!\n📅 {timestamp}")

# Показать все заметки
async def show_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'notes' not in context.user_data or not context.user_data['notes']:
        await update.message.reply_text("📝 У вас пока нет заметок")
        return
    
    notes_text = "📝 Ваши заметки:\n\n"
    for i, note in enumerate(context.user_data['notes'], 1):
        notes_text += f"{i}. {note['text']}\n📅 {note['date']}\n\n"
    
    await update.message.reply_text(notes_text)

# Обработка команды /task
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Использование: /task <описание задачи>")
        return
    
    task_text = ' '.join(context.args)
    
    if 'tasks' not in context.user_data:
        context.user_data['tasks'] = []
    
    context.user_data['tasks'].append({
        'text': task_text,
        'created': datetime.now().strftime("%d.%m.%Y %H:%M"),
        'completed': False
    })
    
    await update.message.reply_text(f"✅ Задача добавлена: {task_text}")

# Показать все задачи
async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'tasks' not in context.user_data or not context.user_data['tasks']:
        await update.message.reply_text("📋 У вас пока нет задач")
        return
    
    tasks_text = "📋 Ваши задачи:\n\n"
    for i, task in enumerate(context.user_data['tasks'], 1):
        status = "✅" if task['completed'] else "⏳"
        tasks_text += f"{i}. {status} {task['text']}\n📅 {task['created']}\n\n"
    
    await update.message.reply_text(tasks_text)

# Обработка команды /ask - вопрос к AI
async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    text = update.message.text
    
    if text == "💬 Спросить AI":
        await update.message.reply_text("Задайте ваш вопрос AI, используя команду:\n/ask <ваш вопрос>")
    
    elif text == "📝 Заметка":
        await update.message.reply_text("Чтобы добавить заметку:\n/note <текст заметки>\n\nПосмотреть заметки:\n/notes")
    
    elif text == "✅ Задачи":
        await update.message.reply_text("Чтобы добавить задачу:\n/task <описание задачи>\n\nПосмотреть задачи:\n/tasks")
    
    elif text == "🎨 Идея для арта":
        await update.message.reply_text("🤔 Генерирую идею...")
        try:
            prompt = "Предложи креативную идею для 3D-арта или визуализации. Опиши концепт кратко и вдохновляюще на русском языке."
            response = model.generate_content(prompt)
            await update.message.reply_text(f"💡 {response.text}")
        except Exception as e:
            logger.error(f"Ошибка Gemini API: {e}")
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
    
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

def main():
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("note", add_note))
    application.add_handler(CommandHandler("notes", show_notes))
    application.add_handler(CommandHandler("task", add_task))
    application.add_handler(CommandHandler("tasks", show_tasks))
    application.add_handler(CommandHandler("ask", ask_ai))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
