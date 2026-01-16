"""
RAG Orchestrator - Main entry point for generating responses
Coordinates routing, retrieval, and answer generation
"""
from typing import Optional
from twuaqirag.rag.router import route_message
from twuaqirag.rag.memory import store, ConversationState
from twuaqirag.rag.answer import generate_answer, AnswerInput
from twuaqirag.rag.rag_types import Intent
from twuaqirag.retrieval.vector_store import get_retriever, vector_store


async def generate_response(user_message: str, session_id: str = "default") -> str:
    """
    Main RAG orchestration function.
    
    Args:
        user_message: The user's input message
        session_id: Session identifier for conversation history
        
    Returns:
        Generated response string
    """
    # Get or create conversation state
    if session_id not in store:
        state = ConversationState()
    else:
        state = store[session_id]
    
    # Route the message to determine intent and language
    decision = route_message(user_message, state)
    
    # Update state with detected language
    state.last_lang = decision.response_lang
    if decision.intent in [Intent.PLACE_QUERY, Intent.FACILITY_QUERY] and decision.place_query:
        state.last_place_query = decision.place_query
    
    # Handle clarification requests
    if decision.needs_clarification:
        store[session_id] = state
        return decision.clarification_question or "Could you please clarify?"
    
    # Retrieve context based on intent
    context = ""
    if decision.intent in [Intent.PLACE_QUERY, Intent.FACILITY_QUERY, Intent.BOOTCAMP_QUERY]:
        try:
            retriever = get_retriever(vector_store, lang=decision.response_lang.value)
            docs = retriever.invoke(decision.place_query or user_message)
            # Combine retrieved documents into context
            context = "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            context = f"Error retrieving information: {str(e)}"
    
    elif decision.intent == Intent.DIRECTIONS:
        # For directions, retrieve information about both origin and destination
        try:
            retriever = get_retriever(vector_store, lang=decision.response_lang.value)
            docs = retriever.invoke(user_message)
            context = "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            context = f"Error retrieving directions: {str(e)}"
    
    # Generate answer using LLM
    answer_input = AnswerInput(
        question=user_message,
        context=context,
        response_lang=decision.response_lang,
    )
    
    response = await generate_answer(answer_input)
    
    # Save updated state
    store[session_id] = state
    
    return response

    # # ✅ REVIEW handling (EARLY EXIT)
    # if decision.intent == Intent.REVIEW:
    #  review_agent = user_review_agent()
    #  sentiment = review_agent.evaluate(user_message)

    #  review_service.store_review(
    #     text=user_message,
    #     sentiment=sentiment,
    #     place_id=state.last_place_id or "unknown",
    #     session_id=session_id,
    # )

    #  store[session_id] = state

    #  return (
    #     "شكراً لمشاركتك رأيك. تم تسجيل الملاحظة."
    #     if decision.response_lang.value == "ar"
    #     else "Thank you for your feedback. Your review has been recorded."
    # )
    # Update state with detected language
    



    
    #  state.pending_intent = decision.intent
    #  state.pending_query = decision.place_query or user_message
    #  store[session_id] = state
    #  return decision.clarification_question or "Could you please clarify?"

    # # ✅ Resume pending query after clarification
    # if not decision.place_query and hasattr(state, "pending_query"):
    #  decision.place_query = state.pending_query
    #  decision.intent = state.pending_intent

    
   