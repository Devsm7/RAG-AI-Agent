from datetime import datetime
import logging
from typing import Optional

from .repository import ReviewRepository
from .models import Review
from .email_service import Email_Service
from twuaqirag.rag.rag_types import ReviewSentiment

logger = logging.getLogger(__name__)


class ReviewService:
    def __init__(
        self,
        repository: ReviewRepository,
        email_service: Optional[Email_Service] = None,
    ):
        self.repository = repository
        self.email_service = email_service or Email_Service()

    def store_review(
        self,
        text: str,
        sentiment: ReviewSentiment,
        place_id: str,
        session_id: str,
        place_name: Optional[str] = None,
    ) -> Review:
        review = Review(
            text=text,
            sentiment=sentiment,
            place_id=place_id,
            session_id=session_id,
            created_at=datetime.utcnow(),
        )

        self.repository.add_review(review)

        if sentiment == ReviewSentiment.NEGATIVE:
            self.email_service.send_alert(review, place_name)

        return review
