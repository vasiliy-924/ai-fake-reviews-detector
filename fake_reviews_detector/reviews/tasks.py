from celery import shared_task
from django.conf import settings

from .ml.bert_model import load_model, predict_fake
from .models import AnalysisResult, Review


@shared_task(bind=True)
def analyze_review(self, review_id):
    try:
        # Перенес загрузку модели ВНУТРЬ задачи
        model, tokenizer = load_model()  # <-- Исправление 1

        review = Review.objects.get(id=review_id)
        prob = predict_fake(review.text, model, tokenizer)
        is_fake = prob > 0.5

        # для обучения модели
        # if review.reputation < 1 and review.source == "otzovik":
        #     is_fake = True
        #     prob = 0.8

        result = AnalysisResult.objects.create(
            review=review,
            is_fake=is_fake,
            probability=prob,
            details={
                "model": "RuBERT",
                "reputation_checked": review.reputation < 2},
        )
        return str(result.id)

    except Exception as e:
        logger = self.get_logger()  # <-- Исправление 2
        logger.error(f"Error: {str(e)}")
        raise
