from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import AnalysisResult, Review
from .tasks import analyze_review

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
            'details': result.details
        })
    except AnalysisResult.DoesNotExist:
        return Response({'status': 'pending'}, status=202)
