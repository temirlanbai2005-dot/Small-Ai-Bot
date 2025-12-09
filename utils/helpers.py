"""
Вспомогательные функции
"""

from datetime import datetime, timedelta
import re
from typing import Optional

def format_number(num: int) -> str:
    """
    Форматирование числа с разделителями тысяч
    1234567 -> 1,234,567
    """
    return "{:,}".format(num).replace(',', ' ')

def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Обрезка текста до указанной длины
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rstrip() + suffix

def parse_datetime(date_str: str, time_str: str) -> Optional[datetime]:
    """
    Парсинг даты и времени из строк
    date_str: '25.12.2024'
    time_str: '15:30'
    """
    try:
        dt_str = f"{date_str} {time_str}"
        return datetime.strptime(dt_str, "%d.%m.%Y %H:%M")
    except ValueError:
        return None

def is_weekend(date: datetime = None) -> bool:
    """
    Проверка, является ли день выходным
    """
    if date is None:
        date = datetime.now()
    return date.weekday() >= 5  # 5 = Saturday, 6 = Sunday

def time_until(target_time: datetime) -> str:
    """
    Человекочитаемое время до события
    """
    now = datetime.now()
    delta = target_time - now
    
    if delta.total_seconds() < 0:
        return "прошло"
    
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    if days > 0:
        return f"через {days} д. {hours} ч."
    elif hours > 0:
        return f"через {hours} ч. {minutes} мин."
    else:
        return f"через {minutes} мин."

def extract_hashtags(text: str) -> list:
    """
    Извлечение хештегов из текста
    """
    return re.findall(r'#\w+', text)

def clean_html(text: str) -> str:
    """
    Удаление HTML тегов из текста
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def validate_url(url: str) -> bool:
    """
    Валидация URL
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def split_message(text: str, max_length: int = 4096) -> list:
    """
    Разбиение длинного сообщения на части
    """
    if len(text) <= max_length:
        return [text]
    
    parts = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break
        
        # Ищем ближайший перенос строки
        split_pos = text.rfind('\n', 0, max_length)
        if split_pos == -1:
            split_pos = max_length
        
        parts.append(text[:split_pos])
        text = text[split_pos:].lstrip()
    
    return parts

def sanitize_filename(filename: str) -> str:
    """
    Очистка имени файла от недопустимых символов
    """
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def get_file_extension(filename: str) -> str:
    """
    Получение расширения файла
    """
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

def format_duration(seconds: int) -> str:
    """
    Форматирование длительности в читаемый вид
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"
