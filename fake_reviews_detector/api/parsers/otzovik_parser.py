import os
import re
import logging
import requests
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup
from typing import List, Dict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from reviews.models import DebugLog

# Настройка логгера
logger = logging.getLogger(__name__)

def validate_otzovik_url(url: str) -> None:
    """Проверяет корректность URL Отзовик с помощью регулярного выражения."""
    pattern = r'^https://(www\.)?otzovik\.com/reviews/[a-zA-Z0-9_-]+/?$'
    if not re.match(pattern, url):
        raise ValidationError(
            "Некорректный URL. Пример: https://otzovik.com/reviews/film_nastupit_leto_2024/"
        )

def fetch_otzovik_reviews(product_url: str) -> List[Dict]:
    """
    Парсер отзывов с сайта Отзовик с использованием ScraperAPI.
    Запрашиваем рендеренную страницу и извлекаем отзывы и рейтинги пользователей.
    Личные данные не сохраняются.
    """
    validate_otzovik_url(product_url)
    
    scraperapi_key = os.getenv('SCRAPERAPI_KEY')
    if not scraperapi_key:
        raise ValidationError("Отсутствует API-ключ ScraperAPI")
    
    # Настройка сессии с повторными попытками
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/91.0.4472.124 Safari/537.36'),
        'Accept-Language': 'ru-RU,ru;q=0.9'
    }
    
    try:
        logger.info(f"Starting parser for: {product_url} using ScraperAPI")
        response = session.get(
            'https://api.scraperapi.com',
            params={
                'api_key': scraperapi_key,
                'url': product_url,
                'render': 'true'
            },
            headers=headers,
            timeout=120
        )
        response.raise_for_status()
        
        logger.debug(f"Response status: {response.status_code}, size: {len(response.text)} bytes")
        
        # Сохранение HTML для отладки (можно удалить, если не нужно)
        with open("debug_otzovik.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        DebugLog.objects.create(  # Сохраняем HTML в DebugLog
            html_content=response.text,
            success=True
        )
        
        soup = BeautifulSoup(response.text, 'lxml')
        reviews = []
        
        # Используем селектор для поиска блоков с отзывами.
        # На основании анализа debug_otzovik.html подберите актуальные селекторы.
        items = soup.select('div[itemtype="http://schema.org/Review"]')
        logger.info(f"Found {len(items)} review elements")

        for idx, item in enumerate(items):
            try:
                # Новый селектор текста отзыва: .review-teaser
                text_elem = item.select_one('.review-teaser')
                # Новый селектор рейтинга: span в .rating-score
                rating_elem = item.select_one('.rating-score span')

                if not text_elem or not rating_elem:
                    logger.debug(f"Review #{idx} пропущен: отсутствует текст или рейтинг")
                    continue

                text = text_elem.get_text(strip=True)
                rating_raw = rating_elem.get_text(strip=True)
                try:
                    rating = float(rating_raw.replace(',', '.'))
                except ValueError:
                    logger.debug(f"Review #{idx} ошибка преобразования рейтинга: {rating_raw}")
                    continue

                logger.debug(f"Review #{idx}: Rating {rating}, Text: {text[:50]}...")

                reviews.append({
                    'text': text,
                    'rating': rating,
                    'source': 'otzovik',
                    'url': product_url
                })
            except Exception as e:
                logger.warning(f"Error parsing review #{idx}: {str(e)}")
                continue
                
        return reviews[:50]
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}", exc_info=True)
        raise ValidationError(f"Ошибка парсера: {str(e)}")
    
    except Exception as e:
        DebugLog.objects.create(
            html_content=response.text if 'response' in locals() else '',
            success=False,
            error_message=str(e)
        )
        raise ValidationError(f"Неожиданная ошибка: {str(e)}")
