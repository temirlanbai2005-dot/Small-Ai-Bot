"""
Сервис перевода текста
"""

import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

# Инициализация переводчиков
translator_to_ru = GoogleTranslator(source='en', target='ru')
translator_to_en = GoogleTranslator(source='ru', target='en')

async def translate_to_russian(text: str) -> str:
    """
    Перевод текста на русский
    """
    try:
        # Разбиваем длинный текст на части (лимит Google Translate - 5000 символов)
        max_length = 4500
        
        if len(text) <= max_length:
            return translator_to_ru.translate(text)
        
        # Разбиваем по предложениям
        sentences = text.split('. ')
        translated_parts = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    translated_parts.append(translator_to_ru.translate(current_chunk))
                current_chunk = sentence + '. '
        
        if current_chunk:
            translated_parts.append(translator_to_ru.translate(current_chunk))
        
        return ' '.join(translated_parts)
    
    except Exception as e:
        logger.error(f"Ошибка перевода на русский: {e}")
        return text  # Возвращаем оригинал в случае ошибки

async def translate_to_english(text: str) -> str:
    """
    Перевод текста на английский
    """
    try:
        max_length = 4500
        
        if len(text) <= max_length:
            return translator_to_en.translate(text)
        
        sentences = text.split('. ')
        translated_parts = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    translated_parts.append(translator_to_en.translate(current_chunk))
                current_chunk = sentence + '. '
        
        if current_chunk:
            translated_parts.append(translator_to_en.translate(current_chunk))
        
        return ' '.join(translated_parts)
    
    except Exception as e:
        logger.error(f"Ошибка перевода на английский: {e}")
        return text

async def detect_language(text: str) -> str:
    """
    Определение языка текста
    """
    try:
        # Простая проверка на основе символов
        russian_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
        total_chars = sum(1 for c in text if c.isalpha())
        
        if total_chars == 0:
            return 'unknown'
        
        russian_percentage = russian_chars / total_chars
        
        if russian_percentage > 0.3:
            return 'ru'
        else:
            return 'en'
    
    except Exception as e:
        logger.error(f"Ошибка определения языка: {e}")
        return 'unknown'
