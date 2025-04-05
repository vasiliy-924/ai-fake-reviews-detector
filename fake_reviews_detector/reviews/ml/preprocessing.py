import re
import pandas as pd
from reviews.models import Review

class TextCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r'[^\w\s\.,!?\-–—]', '', text, flags=re.UNICODE)  # Сохраняем пунктуацию
        text = re.sub(r'\s+', ' ', text).strip().lower()
        return text

class DatasetBuilder:
    @classmethod
    def build_dataframe(cls, min_text_length=50):
        queryset = Review.objects.filter(is_verified=True)  # Только проверенные
        data = []
        for review in queryset:
            if len(review.text) < min_text_length:
                continue
            data.append({
                'text': TextCleaner.clean_text(review.text),
                'label': int(review.is_fake),  # 0 - real, 1 - fake
                'rating': review.rating,
                'source': review.source
            })
        return pd.DataFrame(data)