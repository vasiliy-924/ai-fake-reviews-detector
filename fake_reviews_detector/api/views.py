from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Review
from .tasks import analyze_review

@api_view(['POST'])
def check_review_api(request):
    text = request.data.get('text', '')
    if not text:
        return Response({'error': 'Text is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    review = Review.object.create(text=text, source='API')
    analyze_review.delay(review.id)
    return Response({'id': review.id, 'status': 'processing'}, status=status.HTTP_201_CREATED)
