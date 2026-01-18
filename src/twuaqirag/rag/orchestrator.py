"""
RAG Orchestrator
Coordinates routing, retrieval, reviews, and answer generation
"""
import re
import logging
from typing import Optional, Tuple

from twuaqirag.rag.router import route_message
from twuaqirag.rag.memory import store, ConversationState
from twuaqirag.rag.answer import generate_answer, AnswerInput, translate_to_english
from twuaqirag.rag.rag_types import Intent, ResponseLang
from twuaqirag.retrieval.vector_store import get_retriever, vector_store
from twuaqirag.retrieval.formatting import docs_to_context
from twuaqirag.rag.user_review_agent import user_review_agent

from twuaqirag.domain.reviews.repository import ReviewRepository
from twuaqirag.domain.reviews.service import ReviewService
from twuaqirag.domain.reviews.email_service import Email_Service
from twuaqirag.core.config import config

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Review infrastructure
# --------------------------------------------------

review_repository = ReviewRepository(csv_path=config.REVIEWS_CSV)
email_service = Email_Service()

review_service = ReviewService(
    repository=review_repository,
    email_service=email_service,
)


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def extract_place_mention(text: str, response_lang: ResponseLang) -> Optional[Tuple[str, str]]:
    """
    Extract place mention from review text.
    
    Args:
        text: Review text that might contain place names
        response_lang: Language for retrieval
        
    Returns:
        Tuple of (place_id, place_name) if found, None otherwise
    """
    text_lower = text.lower()
    
    # Pattern 1: Room codes (B1-3, B0-1, etc.)
    room_pattern = r'\b[bB]\d+-\d+\b'
    room_match = re.search(room_pattern, text)
    
    if room_match:
        room_name = room_match.group(0).upper()
        logger.info(f"Detected room mention: {room_name}")
        
        # Search for this room
        try:
            retriever = get_retriever(vector_store, lang=response_lang.value)
            docs = retriever.invoke(room_name)
            
            if docs and docs[0].metadata.get('place_id'):
                place_id = docs[0].metadata['place_id']
                place_name = docs[0].metadata.get('name', room_name)
                logger.info(f"Matched room {room_name} to place_id={place_id}")
                return (place_id, place_name)
        except Exception as e:
            logger.error(f"Error searching for room {room_name}: {e}")
    
    # Pattern 2: Named places (Dunkin, Subway, etc.)
    place_keywords = [
        'dunkin', 'subway', 'saldwich', 'maps cafe', 'cafeteria',
        'prayer room', 'toilet', 'elevator', 'reception',
        'دانكن', 'صب واي', 'مقهى', 'كافتيريا', 'مصلى', 'دورة مياه'
    ]
    
    for keyword in place_keywords:
        if keyword in text_lower:
            logger.info(f"Detected place keyword: {keyword}")
            
            try:
                retriever = get_retriever(vector_store, lang=response_lang.value)
                docs = retriever.invoke(keyword)
                
                if docs and docs[0].metadata.get('place_id'):
                    place_id = docs[0].metadata['place_id']
                    place_name = docs[0].metadata.get('name', keyword)
                    logger.info(f"Matched keyword '{keyword}' to place_id={place_id}")
                    return (place_id, place_name)
            except Exception as e:
                logger.error(f"Error searching for keyword {keyword}: {e}")
    
    return None


# --------------------------------------------------
# Main entry point
# --------------------------------------------------

async def generate_response(user_message: str, session_id: str = "default") -> str:
    """Main RAG orchestration function."""
    
    # 1️⃣ Load or create state
    state = store.get(session_id) or ConversationState()

    # 2️⃣ Route message
    decision = route_message(user_message, state)
# --------------------------------------------------
    # ✅ REVIEW SUBMIT (EARLY EXIT)
    # --------------------------------------------------
    if decision.intent == Intent.REVIEW_SUBMIT:
        review_agent = user_review_agent()
        sentiment = review_agent.evaluate(user_message)

        # 🎯 SMART PLACE DETECTION
        # First, try to extract place from review text
        detected_place = extract_place_mention(user_message, decision.response_lang)
        
        if detected_place:
            place_id, place_name = detected_place
            logger.info(f"Using detected place from review text: {place_name} (ID: {place_id})")
        else:
            # Fallback to last known place from context
            place_id = state.last_place_id or "unknown"
            place_name = state.last_place_query
            
            if place_id == "unknown":
                logger.warning(f"Review submitted without place context: {user_message[:50]}...")

        # Store review WITH place_name (for email alerts)
        review_service.store_review(
            text=user_message,
            sentiment=sentiment,
            place_id=place_id,
            session_id=session_id,
            place_name=place_name,  # 👈 ADD THIS LINE!
        )

        store[session_id] = state

        # Return contextual response
        if decision.response_lang == ResponseLang.ARABIC:
            if place_name and place_id != "unknown":
                return f"شكراً لمشاركتك رأيك عن {place_name}. تم تسجيل الملاحظة ({sentiment.value})."
            return f"شكراً لمشاركتك رأيك. تم تسجيل الملاحظة ({sentiment.value})."
        else:
            if place_name and place_id != "unknown":
                return f"Thank you for your feedback about {place_name}. Your review has been recorded ({sentiment.value})."
            return f"Thank you for your feedback. Your review has been recorded ({sentiment.value})."









    # --------------------------------------------------
    # ✅ REVIEW QUERY (EARLY EXIT) - FIXED!
    # --------------------------------------------------
    if decision.intent == Intent.REVIEW_QUERY:
        # 🎯 FIRST: Check if user mentioned a specific place in their query
        # e.g., "are there any reviews for dunkin"
        detected_place = extract_place_mention(user_message, decision.response_lang)
        
        if detected_place:
            # User asked about a specific place
            place_id, place_name = detected_place
            logger.info(f"Review query for specific place: {place_name} (ID: {place_id})")
        else:
            # Fallback to last known place from context
            place_id = state.last_place_id
            place_name = state.last_place_query
            logger.info(f"Review query using context: {place_name} (ID: {place_id})")

        # Guard: no known place yet
        if not place_id:
            return (
                "عن أي مكان تقصد؟ اسأل عن مكان أولاً."
                if decision.response_lang == ResponseLang.ARABIC
                else "Which place are you asking about? Please ask about a location first."
            )

        # Fetch reviews and statistics
        reviews = review_repository.list_by_place(place_id)
        stats = review_repository.get_place_statistics(place_id)

        if not reviews:
            return (
                f"لا توجد مراجعات لـ {place_name or 'هذا المكان'} بعد."
                if decision.response_lang == ResponseLang.ARABIC
                else f"There are no reviews for {place_name or 'this location'} yet."
            )

        # Format response with statistics
        if decision.response_lang == ResponseLang.ARABIC:
            response = f"**تقييمات {place_name or 'المكان'}:**\n\n"
            response += f"📊 إجمالي: {stats['total']}\n"
            response += f"✅ إيجابية: {stats['positive']}\n"
            response += f"➖ محايدة: {stats['neutral']}\n"
            response += f"❌ سلبية: {stats['negative']}\n\n"
            response += "**آخر التعليقات:**\n"
            for r in reviews[-5:]:
                emoji = "✅" if r.sentiment.value == "positive" else "❌" if r.sentiment.value == "negative" else "➖"
                response += f"{emoji} {r.text}\n"
        else:
            response = f"**Reviews for {place_name or 'this location'}:**\n\n"
            response += f"📊 Total: {stats['total']}\n"
            response += f"✅ Positive: {stats['positive']}\n"
            response += f"➖ Neutral: {stats['neutral']}\n"
            response += f"❌ Negative: {stats['negative']}\n\n"
            response += "**Recent Comments:**\n"
            for r in reviews[-5:]:
                emoji = "✅" if r.sentiment.value == "positive" else "❌" if r.sentiment.value == "negative" else "➖"
                response += f"{emoji} {r.text}\n"
        
        return response

    # --------------------------------------------------
    # 3️⃣ Update basic state
    # --------------------------------------------------
    state.last_lang = decision.response_lang

    if decision.place_query:
        state.last_place_query = decision.place_query

    # --------------------------------------------------
    # 4️⃣ Clarification handling
    # --------------------------------------------------
    if decision.needs_clarification:
        state.pending_intent = decision.intent
        state.pending_query = decision.place_query or user_message
        store[session_id] = state
        return decision.clarification_question or "Could you please clarify?"

    # Resume pending query
    if not decision.place_query and hasattr(state, "pending_query"):
        decision.place_query = state.pending_query
        decision.intent = state.pending_intent
        # Clear pending state
        if hasattr(state, "pending_query"):
            delattr(state, "pending_query")
        if hasattr(state, "pending_intent"):
            delattr(state, "pending_intent")

    # --------------------------------------------------
    # 5️⃣ Retrieval
    # --------------------------------------------------
    context = ""

    if decision.intent in {
        Intent.PLACE_QUERY,
        Intent.FACILITY_QUERY,
        Intent.BOOTCAMP_QUERY,
        Intent.DIRECTIONS,
    }:
        retrieval_query = decision.place_query or user_message
        retrieval_lang = decision.response_lang.value
        
        # Cross-Lingual Retrieval for Arabic
        if decision.response_lang == ResponseLang.ARABIC:
            try:
                # Since embedding model struggles with Arabic, we translate query to English
                # and search against English documents (which are semantically richer for this model)
                logger.info(f"Translating Arabic query to English: {retrieval_query}")
                translated_query = await translate_to_english(retrieval_query)
                if translated_query:
                    logger.info(f"Translated query: {translated_query}")
                    retrieval_query = translated_query
                    retrieval_lang = "en"  # Force search in English
            except Exception as e:
                logger.error(f"Translation failed, falling back to Arabic retrieval: {e}")

        retriever = get_retriever(
            vector_store,
            lang=retrieval_lang,
        )

        docs = retriever.invoke(retrieval_query)

        # Convert docs → context
        context = docs_to_context(docs)

        # ✅ CRITICAL: remember place_id for follow-ups & reviews
        if docs:
            for d in docs:
                place_id = d.metadata.get("place_id")
                if place_id:
                    state.last_place_id = place_id
                    logger.info(f"Set last_place_id to: {place_id}")
                    break
            
            # Also store human-readable name if not set
            if not state.last_place_query and docs[0].metadata.get("name"):
                state.last_place_query = docs[0].metadata["name"]
                logger.info(f"Set last_place_query to: {state.last_place_query}")

    # --------------------------------------------------
    # 6️⃣ Generate answer
    # --------------------------------------------------
    response = await generate_answer(
        AnswerInput(
            question=user_message,
            context=context,
            response_lang=decision.response_lang,
        )
    )

    # --------------------------------------------------
    # 7️⃣ Persist state
    # --------------------------------------------------
    store[session_id] = state
    return response