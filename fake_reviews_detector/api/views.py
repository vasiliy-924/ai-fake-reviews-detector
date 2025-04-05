from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult
from django.http import JsonResponse

from reviews.models import AnalysisResult, Review
from reviews.tasks import analyze_review
from .tasks import parse_reviews_task
from .serializers import ParserTriggerSerializer

@api_view(['POST'])
def check_review_api(request):
    text = request.data.get('text', '')
    if not text:
        return Response({'error': 'Text is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    review = Review.objects.create(text=text, source='API')
    analyze_review.delay(review.id)
    
    return Response({'id': review.id, 'status': 'processing'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_result(request, result_id):
    try:
        result = AnalysisResult.objects.get(id=result_id)
        return Response({
            'status': 'complete',
            'is_fake': result.is_fake,
            'probability': result.probability,
            'details': result.details,
            'result_id': str(result.id)
        })
    except AnalysisResult.DoesNotExist:
        return Response({'status': 'pending'}, status=status.HTTP_200_OK)

def task_status(request, task_id):
    task = AsyncResult(task_id)
    return JsonResponse({
        'status': task.status,
        'result': task.result if task.ready() else None
    })

class ParseTriggerAPI(APIView):
    def post(self, request):
        serializer = ParserTriggerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        url = serializer.validated_data['url']
        task = parse_reviews_task.delay(url)  # Запуск задачи
        
        return Response({'task_id': task.id}, status=202)
    
@api_view(['GET'])
def task_status_api(request, task_id):
    """API для проверки статуса задачи Celery"""
    task = AsyncResult(task_id)
    
    response_data = {
        'status': task.status,
        'result': task.result if task.ready() else None
    }
    
    if task.failed():
        response_data['error'] = str(task.result)
    
    return Response(response_data)