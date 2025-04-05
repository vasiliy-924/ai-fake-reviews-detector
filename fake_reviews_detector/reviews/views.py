from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Review
from .tasks import analyze_review
from api.parsers.otzovik_parser import fetch_otzovik_reviews as otzovik_fetch, validate_otzovik_url
from api.tasks import parse_reviews_task

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

@require_http_methods(["GET"])
def fetch_otzovik_reviews_view(request):
    # Получаем URL для получения отзывов через GET-параметр, если он не указан, используем значение по умолчанию
    product_url = request.GET.get('product_url', 'https://otzovik.com/reviews/film_nastupit_leto_2024/')
    
    try:
        # Валидируем URL согласно требованиям Отзовика
        validate_otzovik_url(product_url)
        reviews = otzovik_fetch(product_url)
    except ValidationError as ve:
        return JsonResponse({'error': str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Ошибка при получении отзывов: {str(e)}'}, status=500)

    # Рендерим шаблон с отзывами
    return render(request, 'reviews/otzovik_reviews.html', {'reviews': reviews})

class ParseTriggerFormView(APIView):
    def get(self, request):
        return render(request, 'reviews/trigger_form.html')

    def post(self, request):
        url = request.POST.get('url')
        task = parse_reviews_task.delay(url)
        return JsonResponse({'task_id': task.id})