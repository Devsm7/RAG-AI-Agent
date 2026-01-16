from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from twuaqirag.rag.rag_types import ReviewSentiment


@dataclass
class Review:
    text: str
    sentiment: ReviewSentiment
    place_id: Optional[str]
    session_id: str
    created_at: datetime