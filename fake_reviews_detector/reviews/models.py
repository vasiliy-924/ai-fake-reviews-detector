from django.db import models

class Review(models.Model):
    text = models.TextField(verbose_name='Текст отзыва')
    source = models.CharField(max_length=100, verbose_name='Источник (Яндекс.Маркет и т.д.)')
    rating = models.IntegerField(null=True, blank=True)  # Оценка от 1 до 5
    date_created = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)  # Для разметки вручную

    def __str__(self):
        return f'Отзыв #{self.id}'

class AnalysisResult(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='analisis')
    is_fake = models.BooleanField(verbose_name='Фейковый?')
    probability = models.FloatField(verbose_name='Вероятность (0-1)')
    details = models.JSONField(default=dict)  # Доп. данные (метки, шаблоны)

    def __str__(self):
        return f'Анализ отзыва #{self.review.id}'
