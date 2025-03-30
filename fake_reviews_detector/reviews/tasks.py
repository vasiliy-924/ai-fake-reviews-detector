from celery import shared_task
from .models import Review, AnalysisResult
from .ml.bert_model import load_model, predict_fake

model, tokenizer = load_model()  # Загружаем модель и токенизатор ОДИН РАЗ при старте воркера

@shared_task(bind=True)
def analyze_review(self, review_id):
    try:
        review = Review.objects.get(id=review_id)  # Получаем отзыв из БД
        prob = predict_fake(review.text, model, tokenizer)  # Делаем предсказание
        is_fake = prob > 0.5  # Определяем фейк (порог 0.5)
        result = AnalysisResult.objects.create(  # Сохраняем результат
            review=review,
            is_fake=is_fake,
            probability=prob,
            details={'model': 'RuBERT'}
        )
        return str(result.id)
        
    except Exception as e:
        analyze_review.update_state(  # Логируем ошибку
            state='FAILURE', 
            meta={'exc': str(e)}
        )
        raise