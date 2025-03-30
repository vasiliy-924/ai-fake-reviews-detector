from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Review, AnalysisResult
from .tasks import analyze_review

@require_http_methods(["GET", "POST"])
def check_review_view(request):
    # Обработка AJAX-запроса
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if not text:
            return JsonResponse(
                {'error': 'Введите текст отзыва'}, 
                status=400
            )
        try:
            # Создаём запись в БД
            review = Review.objects.create(
                text=text, 
                source='web_form'
            )

            # Запускаем асинхронную задачу
            task = analyze_review.delay(review.id)
            
            # Возвращаем ID задачи для отслеживания статуса
            return JsonResponse({
                'result_id': task.id,
                'review_id': review.id
            })
            
        except Exception as e:
            return JsonResponse(
                {'error': f'Ошибка сервера: {str(e)}'}, 
                status=500
            )
    
    # GET-запрос: показать пустую форму
    return render(request, 'reviews/check.html')