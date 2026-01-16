"""
Enums/typing (Lang/Intent)
Type definitions for RAG module
"""
from enum import Enum


class Lang(str, Enum):
    """Supported languages"""
    ENGLISH = "en"
    ARABIC = "ar"
    MIXED = "mixed"

class ResponseLang(str, Enum):
    """Response language"""
    ENGLISH = "en"
    ARABIC = "ar"


class ReviewSentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class Intent(str, Enum):
    """User intent types"""
    # Core RAG actions
    PLACE_QUERY = "place_query"          # موقع قاعة / مكان
    BOOTCAMP_QUERY = "bootcamp_query"    # معلومات عن معسكر
    FACILITY_QUERY = "facility_query"    # دورة مياه، كافيه...
    DIRECTIONS = "directions"             # من X إلى Y
    REVIEW = "review"
    # Conversation control
    CLARIFY = "clarify"                   # معلومات ناقصة (وينه؟)
    TIME_QUERY = "time_query"             # وقت / دوام
    GENERAL_QUERY = "general_query"   
        # خارج النطاق
