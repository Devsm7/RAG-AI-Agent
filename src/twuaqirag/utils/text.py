"""
Text processing helpers
Utilities for text normalization and cleaning
"""
import re
from typing import Optional


def normalize_arabic(text: str) -> str:
    """
    Normalize Arabic text
    
    Args:
        text: Input Arabic text
        
    Returns:
        Normalized text
    """
    # Normalize Arabic characters
    text = re.sub("[إأآا]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ؤ", "ء", text)
    text = re.sub("ئ", "ء", text)
    text = re.sub("ة", "ه", text)
    
    # Remove diacritics
    text = re.sub("[\u064B-\u0652]", "", text)
    
    return text


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def is_arabic(text: str) -> bool:
    """
    Check if text contains Arabic characters
    
    Args:
        text: Input text
        
    Returns:
        True if text contains Arabic characters
    """
    return any('\u0600' <= char <= '\u06FF' for char in text)


def extract_time(text: str) -> Optional[str]:
    """
    Extract time from text
    
    Args:
        text: Input text
        
    Returns:
        Extracted time or None
    """
    # Match time patterns like "14:00", "2:30 PM", etc.
    time_pattern = r'\b(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?\b'
    match = re.search(time_pattern, text)
    
    if match:
        return match.group(0)
    
    return None


def convert_24h_to_12h(time_str: str, lang: str = "en") -> str:
    """
    Convert 24-hour time format to 12-hour format
    
    Args:
        time_str: Time string in 24-hour format (e.g., "14:00")
        lang: Language code ("en" or "ar")
        
    Returns:
        Time string in 12-hour format
    """
    try:
        hour, minute = map(int, time_str.split(':'))
        
        if hour == 0:
            hour_12 = 12
            period = "AM" if lang == "en" else "صباحاً"
        elif hour < 12:
            hour_12 = hour
            period = "AM" if lang == "en" else "صباحاً"
        elif hour == 12:
            hour_12 = 12
            period = "PM" if lang == "en" else "مساءً"
        else:
            hour_12 = hour - 12
            period = "PM" if lang == "en" else "مساءً"
        
        return f"{hour_12}:{minute:02d} {period}"
    except:
        return time_str
