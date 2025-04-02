from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Review, AnalysisResult
from .tasks import analyze_review
from fake_reviews_detector.api.parsers.otzovik_parser import fetch_ozon_reviews

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
            review = Review.objects.create(  # Создаём запись в БД
                text=text, 
                source='web_form'
            )

            task = analyze_review.delay(review.id)  # Запускаем асинхронную задачу
            
            return JsonResponse({  # Возвращаем ID задачи для отслеживания статуса
                'task_id': task.id,
                'review_id': review.id
            })
            
        except Exception as e:
            return JsonResponse(
                {'error': f'Ошибка сервера: {str(e)}'}, 
                status=500
            )
    
    # GET-запрос: показать пустую форму
    return render(request, 'reviews/check.html')

def show_ozon_reviews(request):
    product_url = "https://www.ozon.ru/product/ваш-id-товара/"
    try:
        reviews = fetch_ozon_reviews(product_url)
    except Exception as e:
        reviews = []
    
    return render(request, 'reviews/ozon_reviews.html', {
        'reviews': reviews
    })
