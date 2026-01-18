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

    @classmethod
    def from_dict(cls, row: dict) -> "Review":
        return cls(
            text=row["text"],
            sentiment=ReviewSentiment(row["sentiment"]),
            place_id=row["place_id"],
            session_id=row["session_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
