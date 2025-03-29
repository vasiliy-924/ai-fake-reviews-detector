from celery import shared_task
from .ml.bert_model import load_model, predict_fake
from .models import Review, AnalysisResult

model, tokenizer = load_model()

@shared_task
def analyze_review(review_id):
    review = Review.objects.get(id=review_id)
    prob = predict_fake(review.text)  # Важно: функция должна возвращать число (0.0-1.0)
    is_fake = prob > 0.7
    # Создаём и возвращаем результат
    result = AnalysisResult.objects.create(
        review=review,
        is_fake=is_fake,
        probability=prob,
        details={'model': 'RuBERT'}
    )
    return result.id  # Возвращаем ID результата (или prob)