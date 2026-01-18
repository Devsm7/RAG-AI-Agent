"""
ConversationState + store
Memory management for conversation history
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from .rag_types import ResponseLang

Intent = Literal["place", "bootcamp", "facility", "directions", "time", "unknown"]

class ConversationState(BaseModel):
    last_lang: ResponseLang = ResponseLang.ENGLISH
    last_intent: Intent = "unknown"

    # آخر شيء تم “حله” فعليًا (IDs ثابتة)
    last_place_id: Optional[int] = None
    last_bootcamp_id: Optional[int] = None  # جديد ومهم

    # للاتجاهات
    last_origin_id: Optional[int] = None
    last_destination_id: Optional[int] = None

    # آخر استعلامات نصية (للتتبع فقط)
    last_query_text: Optional[str] = None

    # candidates لو فيه أكثر من match (لـ clarification)
    last_place_candidates: List[int] = Field(default_factory=list)
    last_bootcamp_candidates: List[int] = Field(default_factory=list)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

class InMemoryStateStore:
    def __init__(self):
        self._store: dict[str, ConversationState] = {}

    def get(self, session_id: str) -> ConversationState:
        if session_id not in self._store:
            self._store[session_id] = ConversationState()
        return self._store[session_id]

    def set(self, session_id: str, state: ConversationState):
        state.updated_at = datetime.utcnow()
        self._store[session_id] = state

store = InMemoryStateStore()
