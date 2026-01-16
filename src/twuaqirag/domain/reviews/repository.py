from typing import List
from .models import Review


class ReviewRepository:

    def __init__(self):
        self._reviews: List[Review] = []

    def add_review(self,review:Review) -> None:
        self._reviews.append(review)

    def list_all(self) -> List[Review]:
        return list(self._reviews)
    
    def list_by_place(self, place_id: str) -> List[Review]:
        return [r for r in self._reviews if r.place_id == place_id]
    
    