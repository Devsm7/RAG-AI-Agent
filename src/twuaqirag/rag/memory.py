"""
ConversationState + store
Memory management for conversation history
"""
from pydantic import BaseModel
from typing import Optional
from .types import ResponseLang

class ConversationState(BaseModel):
    last_lang: ResponseLang = "en"

    last_place_query: Optional[str] = None

    # للاتجاهات
    last_origin_query: Optional[str] = None
    last_destination_query: Optional[str] = None

    # لاحقًا لما نضيف place_id resolver
    last_place_id: Optional[str] = None
    last_origin_id: Optional[str] = None
    last_destination_id: Optional[str] = None

class InMemoryStateStore:

    def __init__(self):
        self._store: dict[str, ConversationState] = {}

    def get(self , session_id: str) -> Optional[ConversationState]:
        if session_id not in self._store:
            self._store[session_id] = ConversationState()
        return self._store[session_id]

    def set(self, session_id: str, state: ConversationState):
        self._store[session_id] = state