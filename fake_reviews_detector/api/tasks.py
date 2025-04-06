import logging

from celery import shared_task
from django.db import transaction
from reviews.models import Review

from .parsers.otzovik_parser import fetch_otzovik_reviews

logger = logging.getLogger(__name__)


@shared_task
@transaction.atomic  # Для атомарности операций
def parse_and_save_otzovik_reviews(url: str) -> str:
    try:
        reviews = fetch_otzovik_reviews(url)
        created_count = 0

        for review in reviews:
            obj, created = Review.objects.update_or_create(
                text=review["text"],
                source=review["source"],
                defaults={
                    "rating": review["rating"],
                    "meta": {"url": review["url"]},  # Дополнительные данные
                },
            )
            if created:
                created_count += 1

        return f"Добавлено: {created_count}, Обновлено: {len(reviews) - created_count}"

    except Exception as e:
        logger.error(f"Ошибка в задаче: {str(e)}", exc_info=True)
        return f"Критическая ошибка: {str(e)}"


@shared_task
def parse_reviews_task(url: str):
    try:
        reviews = fetch_otzovik_reviews(url)
        for data in reviews:
            # Сохраняем отзыв, избегая дубликатов
            Review.objects.get_or_create(
                text=data["text"],
                source=data["source"],
                defaults={
                    "rating": data["rating"], "meta": {
                        "url": data["url"]}},
            )
        return {  # Возвращаем структурированные данные!
            "status": "success",
            "reviews": reviews,  # Список отзывов
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
