"""
Генератор контента для постов в соцсетях
"""

import logging
from services.gemini_ai import ask_gemini
from config.platforms import get_platform_config, get_recommended_hashtags

logger = logging.getLogger(__name__)

async def generate_post_idea(platform: str = None) -> str:
    """
    Генерация идеи для поста
    """
    platform_info = ""
    if platform:
        config = get_platform_config(platform)
        platform_info = f"""
Платформа: {platform}
Аудитория: {config.get('audience', 'общая')}
Тип контента: {config.get('content_type', 'любой')}
        """
    
    prompt = f"""
Сгенерируй идею для поста 3D-артиста в социальных сетях.

{platform_info}

Идея должна быть:
• Креативной и цепляющей
• Актуальной для 3D-артистов
• Подходящей для визуального контента
• Способной вызвать интерес аудитории

Опиши идею кратко (2-3 предложения) на русском языке.
    """
    
    try:
        idea = await ask_gemini(prompt)
        return idea
    except Exception as e:
        logger.error(f"Ошибка генерации идеи поста: {e}")
        raise

async def generate_full_post(idea: str, platform: str = None, hashtags: bool = True) -> str:
    """
    Генерация полного текста поста на английском
    """
    config = get_platform_config(platform) if platform else {}
    max_length = config.get('max_length', 2000)
    
    hashtag_instruction = ""
    if hashtags:
        hashtag_instruction = f"\n• Добавь 5-10 релевантных хештегов в конце"
    
    prompt = f"""
На основе этой идеи создай готовый пост для {platform or 'социальных сетей'}:

ИДЕЯ: {idea}

Требования:
• Текст на АНГЛИЙСКОМ языке
• Максимум {max_length} символов
• Цепляющее начало
• Эмодзи для визуальной привлекательности
• Призыв к действию (CTA) в конце{hashtag_instruction}
• Тон: дружелюбный, профессиональный

Создай готовый текст поста.
    """
    
    try:
        post = await ask_gemini(prompt)
        
        # Добавляем хештеги если их нет
        if hashtags and '#' not in post:
            tags = get_recommended_hashtags('3d_art', limit=8)
            post += f"\n\n{' '.join(tags)}"
        
        return post
    except Exception as e:
        logger.error(f"Ошибка генерации поста: {e}")
        raise

async def generate_carousel_captions(num_slides: int = 5) -> list:
    """
    Генерация подписей для карусели (Instagram/LinkedIn)
    """
    prompt = f"""
Создай {num_slides} коротких подписей (captions) для карусели постов о 3D-искусстве.

Требования:
• Каждая подпись - 1-2 предложения
• На английском языке
• Образовательный/инсайтовый контент
• Нумерация слайдов

Формат:
1. [текст первого слайда]
2. [текст второго слайда]
...
    """
    
    try:
        response = await ask_gemini(prompt)
        # Парсим ответ
        captions = []
        for line in response.split('\n'):
            if line.strip() and line[0].isdigit():
                caption = line.split('.', 1)[1].strip()
                captions.append(caption)
        
        return captions[:num_slides]
    except Exception as e:
        logger.error(f"Ошибка генерации подписей: {e}")
        return [f"Slide {i+1}" for i in range(num_slides)]

async def generate_story_idea() -> str:
    """
    Генерация идеи для Stories (Instagram/Telegram)
    """
    prompt = """
Предложи идею для короткой истории (Story) для 3D-артиста.

Формат:
• Что показать
• Какой текст/стикеры добавить
• Призыв к действию

Кратко, на русском языке.
    """
    
    try:
        idea = await ask_gemini(prompt)
        return idea
    except Exception as e:
        logger.error(f"Ошибка генерации идеи для Stories: {e}")
        return "Покажи процесс работы над проектом (timelapse), добавь вопрос аудитории и стикер с опросом."
