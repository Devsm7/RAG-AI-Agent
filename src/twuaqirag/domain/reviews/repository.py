from typing import List, Optional
from pathlib import Path
import csv
import logging
from .models import Review

logger = logging.getLogger(__name__)


class ReviewRepository:
    def __init__(self, csv_path: Optional[Path] = None):
        if csv_path is None:
            from twuaqirag.core.config import config
            csv_path = config.PROJECT_ROOT / "datasets" / "reviews.csv"

        # ✅ GUARANTEED ATTRIBUTE
        self.csv_path: Path = Path(csv_path)

        logger.warning(f"🧪 Reviews CSV path: {self.csv_path.resolve()}")

        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.csv_path.exists():
            self._initialize_csv()

    def _initialize_csv(self) -> None:
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["text", "sentiment", "place_id", "session_id", "created_at"]
            )

    def add_review(self, review: Review) -> None:
        if not hasattr(self, "csv_path"):
            raise RuntimeError("ReviewRepository not initialized correctly")

        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    review.text,
                    review.sentiment.value,
                    review.place_id,
                    review.session_id,
                    review.created_at.isoformat(),
                ]
            )

        logger.info(f"✅ Review added for place_id={review.place_id}")

    def list_by_place(self, place_id: str) -> List[Review]:
        reviews: List[Review] = []

        if not self.csv_path.exists():
            return reviews

        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["place_id"] == str(place_id):
                    reviews.append(Review.from_dict(row))

        return reviews

    def get_place_statistics(self, place_id: str) -> dict:
        reviews = self.list_by_place(place_id)

        from collections import Counter

        counts = Counter(r.sentiment.value for r in reviews)

        return {
            "total": len(reviews),
            "positive": counts.get("positive", 0),
            "neutral": counts.get("neutral", 0),
            "negative": counts.get("negative", 0),
        }
