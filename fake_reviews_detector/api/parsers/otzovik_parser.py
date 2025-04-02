# fake_reviews_detector/api/parsers/otzovik_parser.py
import os
import requests
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup

def validate_otzovik_url(url: str) -> None:
    """
    Проверяет, что URL соответствует схеме сайта Отзовик.
    Пример корректного URL: https://otzovik.com/reviews/film_nastupit_leto_2024/
    """
    if 'otzovik.com/reviews/' not in url:
        raise ValidationError("Некорректный URL отзовик. Пример: https://otzovik.com/reviews/film_nastupit_leto_2024/")

def fetch_otzovik_reviews(product_url: str) -> list[dict]:
    """
    Сбор отзывов с сайта Отзовик через ScraperAPI.

    Обрабатывает запрос вида:
      curl "https://api.scraperapi.com?api_key=МОЙ_КЛЮЧ&url=https://otzovik.com/reviews/film_nastupit_leto_2024/"

    Извлекает только текст отзыва и рейтинг (без персональных данных).
    """
    validate_otzovik_url(product_url)
    
    scraperapi_key = os.getenv('SCRAPERAPI_KEY')
    api_url = 'https://api.scraperapi.com'
    
    params = {
        'api_key': scraperapi_key,
        'url': product_url,
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=60)
        response.raise_for_status()
        html = response.text
        
        soup = BeautifulSoup(html, 'html.parser')
        reviews = []
        
        # Ищем все блоки с отзывами
        review_divs = soup.find_all('div', itemprop='review')
        for review in review_divs:
            # Извлекаем текст отзыва
            teaser_div = review.find('div', class_='review-teaser')
            text = teaser_div.get_text(strip=True) if teaser_div else None
            
            # Извлекаем рейтинг отзыва
            rating_div = review.find('div', class_='rating-score')
            rating = None
            if rating_div:
                rating_span = rating_div.find('span')
                if rating_span:
                    try:
                        rating = float(rating_span.get_text(strip=True))
                    except ValueError:
                        rating = None
            
            # Добавляем отзыв, если найдены и текст, и рейтинг
            if text and rating is not None:
                reviews.append({
                    'text': text,
                    'rating': rating,
                    'source': 'otzovik'
                })
        
        return reviews[:20]
    
    except requests.exceptions.RequestException as e:
        raise ValidationError(f'ScraperAPI Error: {str(e)}')
