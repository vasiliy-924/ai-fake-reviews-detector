from celery import shared_task
from .models import Review, AnalysisResult
from .ml.bert_model import load_model, predict_fake

# Загружаем модель и токенизатор ОДИН РАЗ при старте воркера
model, tokenizer = load_model()

@shared_task
def analyze_review(review_id):
    try:
        # Получаем отзыв из БД
        review = Review.objects.get(id=review_id)

        # Делаем предсказание
        prob = predict_fake(review.text, model, tokenizer)
        
        # Определяем фейк (порог 0.5)
        is_fake = prob > 0.5
        
        # Сохраняем результат
        result = AnalysisResult.objects.create(
            review=review,
            is_fake=is_fake,
            probability=prob,
            details={'model': 'RuBERT'}
        )
        return result.id
        
    except Exception as e:
        # Логируем ошибку
        analyze_review.update_state(
            state='FAILURE', 
            meta={'exc': str(e)}
        )
        raise