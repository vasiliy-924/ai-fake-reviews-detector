from django.shortcuts import render
from django.http import JsonResponse
from .models import Review, AnalysisResult  # Явный импорт моделей
from .tasks import analyze_review

def check_review_view(request):
    result = None
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:  # Проверка наличия текста
            review = Review.objects.create(text=text, source='web')
            analyze_review.delay(review.id)
            try:
                result = AnalysisResult.objects.get(review=review)
            except AnalysisResult.DoesNotExist:
                return render(request, 'reviews/check.html', {
                    'error': 'Результат ещё не готов'
                })
    return render(request, 'reviews/check.html', {'result': result})