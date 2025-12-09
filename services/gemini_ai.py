"""
Сервис для работы с Google Gemini AI
"""

import os
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Настройка Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    model = None
    logger.error("❌ GEMINI_API_KEY не установлен!")

async def ask_gemini(prompt: str) -> str:
    """Отправить запрос к Gemini AI"""
    if not model:
        return "❌ AI временно недоступен"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Ошибка Gemini: {e}")
        raise

async def generate_art_idea() -> str:
    """Генерация идеи для арта"""
    prompt = """
Сгенерируй креативную идею для 3D-арта. Включи:
• Концепт
• Стиль (фотореализм, стилизация, low-poly)
• Настроение и цветовую палитру
• Технические советы

Ответ на русском, вдохновляюще, 3-5 предложений.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Ошибка генерации идеи: {e}")
        return "Создай стилизованного персонажа с яркими цветами! 🎨"

async def generate_motivation() -> str:
    """Мотивационное сообщение"""
    prompt = """
Создай короткое мотивационное сообщение для 3D-артиста.
Вдохновляющее, позитивное, 2-3 предложения на русском.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Каждый проект делает тебя лучше. Продолжай создавать! 🚀"

async def generate_project_idea() -> str:
    """Идея для проекта"""
    prompt = """
Предложи идею для небольшого 3D-проекта на 1-3 дня.
Интересная, реалистичная, полезная для портфолио.
2-3 предложения на русском.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Создай стилизованный предмет из повседневной жизни в необычном стиле! 🎨"
