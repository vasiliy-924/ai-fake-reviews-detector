# fake_reviews_detector/api/tasks.py
from celery import shared_task
from .parsers.otzovik_parser import fetch_otzovik_reviews
from reviews.models import Review
import logging

logger = logging.getLogger(__name__)

@shared_task
def parse_and_save_otzovik_reviews(url: str) -> str:
    try:
        reviews = fetch_otzovik_reviews(url)
        for review_data in reviews:
            Review.objects.update_or_create(
                text=review_data["text"],
                defaults={
                    "rating": review_data["rating"],
                    "source": review_data["source"]
                }
            )
        return f"Добавлено {len(reviews)} отзывов"
    except Exception as e:
        return f"Ошибка: {str(e)}"