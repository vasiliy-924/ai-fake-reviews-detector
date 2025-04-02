# fake_reviews_detector/api/tasks.py
from celery import shared_task
from .parsers.otzovik_parser import fetch_ozon_reviews
from reviews.models import Review

@shared_task
def parse_and_save_ozon_reviews(product_id: str):
    """Задача Celery: парсинг через ScraperAPI."""
    try:
        reviews = fetch_ozon_reviews(product_id)
        
        for review_data in reviews:  # Сохранение с проверкой дублей по тексту
            Review.objects.update_or_create(
                text=review_data["text"],
                defaults={
                    "rating": review_data["rating"],
                    "source": review_data["source"]
                }
            )
            
        return f"Сохранено отзывов: {len(reviews)}"
    
    except Exception as e:
        return f"Ошибка: {str(e)}"