import os
import re
import requests
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup
from typing import List, Dict

def validate_otzovik_url(url: str) -> None:
    """Проверяет корректность URL Отзовик с помощью регулярного выражения."""
    pattern = r'^https://(www\.)?otzovik\.com/reviews/[a-zA-Z0-9_-]+/?$'
    if not re.match(pattern, url):
        raise ValidationError(
            "Некорректный URL. Пример: https://otzovik.com/reviews/film_nastupit_leto_2024/"
        )

def fetch_otzovik_reviews(product_url: str) -> List[Dict]:
    """Улучшенный парсер с обработкой ошибок и актуальными селекторами."""
    validate_otzovik_url(product_url)
    
    scraperapi_key = os.getenv('SCRAPERAPI_KEY')
    if not scraperapi_key:
        raise ValidationError("Отсутствует API-ключ ScraperAPI")

    try:
        response = requests.get(
            'https://api.scraperapi.com',
            params={
                'api_key': scraperapi_key,
                'url': product_url,
                'render': 'true',  # Для JS-рендеринга
            },
            timeout=60
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        reviews = []
        
        # Актуальные селекторы (проверьте на реальной странице!)
        for item in soup.select('div.review-item:not(.review-comments)'):
            text_elem = item.select_one('.review-body')
            rating_elem = item.select_one('.rating-value')
            
            if not text_elem or not rating_elem:
                continue
                
            try:
                reviews.append({
                    'text': text_elem.get_text(strip=True),
                    'rating': float(rating_elem.text.strip()),
                    'source': 'otzovik',
                    'url': product_url  # Для отслеживания источника
                })
            except ValueError:
                continue
                
        return reviews[:20]  # Лимит на количество
        
    except requests.exceptions.RequestException as e:
        raise ValidationError(f"Ошибка парсера: {str(e)}")