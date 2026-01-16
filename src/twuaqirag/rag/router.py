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

def route_message(user_msg:str , state: ConversationState) -> RouteDecision:
    lang = detect_lang(user_msg)
    response_lang = pick_response_Lang(lang , user_msg)

    msg = user_msg.strip()
    msg_low = msg.lower()
    # 1) Pronoun / short messages: "وينه؟" "where is it?"
    short_forms_ar = {"وينه", "وينه؟", "وين", "وين؟", "هنا؟", "هناك؟"}
    short_forms_en = {"where is it", "where is it?", "where?", "here?", "there?"}

    if msg_low in short_forms_en or msg in short_forms_ar or len(msg) < 3:
        if state.last_place_query:
            return RouteDecision(
               lang = lang,
               response_lang = response_lang,
               intent = Intent.PLACE_QUERY,
               place_query = state.last_place_query,  
            )

        return RouteDecision(
                lang=lang,
                response_lang=response_lang,
                intent=Intent.CLARIFY,
                needs_clarification=True,
                clarification_question=(
                    "تقصد أي مكان/قاعة؟ اكتب الاسم أو رقم القاعة."
                    if response_lang == "ar"
                    else "Which place/classroom do you mean? Please provide the name or room number."
                ),
    )

    # 2) Directions: "من X إلى Y" "from X to Y"
    direction_forms_ar = {"من", "إلى", "من", "إلى"}
    direction_forms_en = {"from", "to", "from", "to"}

    if msg_low in direction_forms_en or msg in direction_forms_ar:
        return RouteDecision(
                lang=lang,
                response_lang=response_lang,
                intent=Intent.DIRECTIONS,
                origin_query=state.last_origin_query,
                destination_query=state.last_destination_query,
        )


    # 3) Facility queries (اختياري الآن - نوسعها لاحقاً)
    facility_keywords_ar = ["دورة", "حمام", "مقهى", "كافتيريا", "مصلى", "اقرب", "أقرب"]
    facility_keywords_en = ["toilet", "bathroom", "cafe", "cafeteria", "prayer", "nearest", "closest"]

    if any(k in msg for k in facility_keywords_ar) or any(k in msg_low for k in facility_keywords_en):
        return RouteDecision(
                lang=lang,
                response_lang=response_lang,
                intent=Intent.FACILITY_QUERY,
                facility_query=state.last_facility_query,
        )

    return RouteDecision(
        lang=lang,
        response_lang=response_lang,
        intent=Intent.PLACE_QUERY,
        place_query=msg,
    )

    

        
