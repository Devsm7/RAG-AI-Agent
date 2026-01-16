from typing import Optional
from twuaqirag.rag.rag_types import ReviewSentiment
from .repository import ReviewRepository


class ReviewService:
    """
    Handles review-saving logic.
    """

    def __init__(self, repository: ReviewRepository):
        self.repository = repository

    def store_review(
        self,
        *,
        text: str,
        sentiment: ReviewSentiment,
        session_id: str,
        place_id: Optional[str] = None,
    ) -> None:
        # Basic validation (service responsibility)
        if not text or not text.strip():
            return  # do not store empty reviews

        # Save review (repository responsibility)
        self.repository.add(
            text=text,
            sentiment=sentiment,
            session_id=session_id,
            place_id=place_id,
        )

        # Future logic goes here (NOT in orchestrator, NOT in repository)
        # if sentiment == ReviewSentiment.NEGATIVE:
        #     alert_service.send_email(...)
