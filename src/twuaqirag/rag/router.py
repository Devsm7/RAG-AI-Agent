"""
RouteDecision + detect_lang + rules
This module will handle routing logic and language detection
"""

import re
from pydantic import BaseModel
from typing import Optional
from .rag_types import Lang , ResponseLang , Intent
from .memory import ConversationState


_AR_RE = re.compile(r"[\u0600-\u06FF]")## To Detect Arabic language


AR_SHORT = {"وينه", "وين", "هنا", "هناك", "وين؟", "وينه؟", "هنا؟", "هناك؟"}
EN_SHORT = {"where", "where?", "where is it", "where is it?", "here?", "there?"}

FACILITY_AR = ["دورة", "حمام", "مقهى", "كافتيريا", "مصلى", "اقرب", "أقرب", "اقرب شي", "اقرب شيء"]
FACILITY_EN = ["toilet", "bathroom", "restroom", "cafe", "cafeteria", "prayer", "nearest", "closest"]

# Regex directions:
# Arabic: من X إلى Y
RE_DIR_AR = re.compile(r"من\s+(?P<origin>.+?)\s+إلى\s+(?P<dest>.+)", re.UNICODE)
# English: from X to Y
RE_DIR_EN = re.compile(r"from\s+(?P<origin>.+?)\s+to\s+(?P<dest>.+)", re.IGNORECASE)

def _normalize(msg: str) -> str:
    msg = msg.strip()
    msg = msg.replace("؟", "?")
    msg = re.sub(r"\s+", " ", msg)
    return msg

def detect_lang(text:str) -> Lang:
    has_ar = bool(_AR_RE.search(text))
    has_en = bool(re.search(r"[a-zA-Z]",text))

    if has_ar and has_en:
        return Lang.MIXED
    if has_ar:
        return Lang.ARABIC
    return Lang.ENGLISH

def pick_response_Lang(user_lang:Lang , user_text:str) -> ResponseLang:
    if user_lang == Lang.ARABIC:
        return ResponseLang.ARABIC
    if user_lang == Lang.MIXED:
        return ResponseLang.ARABIC if _AR_RE.search(user_text) else ResponseLang.ENGLISH
    return ResponseLang.ENGLISH


class RouteDecision(BaseModel):
    lang: Lang
    response_lang: ResponseLang
    intent: Intent

    place_query: Optional[str] = None
    origin_query: Optional[str] = None
    destination_query: Optional[str] = None

    needs_clarification: bool = False
    clarification_question: Optional[str] = None

def route_message(user_msg: str, state: ConversationState) -> RouteDecision:
    msg = _normalize(user_msg)
    msg_low = msg.lower()

    lang = detect_lang(msg)

    # pick_response_Lang: الأفضل إذا mixed يرجع state.last_lang
    response_lang = pick_response_Lang(lang, msg, last_lang=state.last_lang)

    # 1) Directions parsing (الأهم)
    m_ar = RE_DIR_AR.search(msg)
    if m_ar:
        origin = m_ar.group("origin").strip()
        dest = m_ar.group("dest").strip()
        return RouteDecision(
            lang=lang,
            response_lang=response_lang,
            intent=Intent.DIRECTIONS,
            origin_query=origin,
            destination_query=dest,
        )

    m_en = RE_DIR_EN.search(msg_low)
    if m_en:
        origin = m_en.group("origin").strip()
        dest = m_en.group("dest").strip()
        return RouteDecision(
            lang=lang,
            response_lang=response_lang,
            intent=Intent.DIRECTIONS,
            origin_query=origin,
            destination_query=dest,
        )

    # 2) Short follow-ups: "وين؟" "where?" الخ
    # خله follow-up فقط إذا عندنا last_place_query أو last_* موجودة
    if msg_low in EN_SHORT or msg in AR_SHORT:
        if state.last_place_query:
            return RouteDecision(
                lang=lang,
                response_lang=response_lang,
                intent=Intent.PLACE_QUERY,
                place_query=state.last_place_query,
            )

        return RouteDecision(
            lang=lang,
            response_lang=response_lang,
            intent=Intent.CLARIFY,
            needs_clarification=True,
            clarification_question=(
                "تقصد أي مكان/قاعة؟ اكتب الاسم أو رقم القاعة."
                if response_lang == ResponseLang.ARABIC
                else "Which place/classroom do you mean? Please provide the name or room number."
            ),
        )

    # 3) Facility queries
    if any(k in msg for k in FACILITY_AR) or any(k in msg_low for k in FACILITY_EN):
        return RouteDecision(
            lang=lang,
            response_lang=response_lang,
            intent=Intent.FACILITY_QUERY,
            facility_query=msg,   # ✅ الرسالة الحالية
        )

    # 4) Default: place lookup
    return RouteDecision(
        lang=lang,
        response_lang=response_lang,
        intent=Intent.PLACE_QUERY,
        place_query=msg,
    )

    

        
