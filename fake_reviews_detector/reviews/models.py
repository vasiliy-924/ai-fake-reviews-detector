from django.db import models
from django.urls import reverse
from django_celery_beat.models import PeriodicTask

class Review(models.Model):
    text = models.TextField(verbose_name='Текст отзыва', db_index=True)
    source = models.CharField(max_length=100, verbose_name='Источник')
    rating = models.FloatField(null=True, verbose_name='Оценка')
    meta = models.JSONField(default=dict, verbose_name='Метаданные')  # URL, дата парсинга и т.д.
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_verified = models.BooleanField(default=False, verbose_name='Проверен')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-date_created']
        unique_together = ['text', 'source']  # Запрет дубликатов

    def get_absolute_url(self):
        return reverse('review-detail', args=[str(self.id)])

class AnalysisResult(models.Model):
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='analysis',
        verbose_name='Отзыв'
    )
    is_fake = models.BooleanField(verbose_name='Фейковый')
    probability = models.FloatField(verbose_name='Вероятность')
    model_version = models.CharField(max_length=50, default='v1.0', verbose_name='Версия модели')
    details = models.JSONField(default=dict, verbose_name='Детали')

    class Meta:
        verbose_name = 'Результат анализа'
        verbose_name_plural = 'Результаты анализов'

class ParserConfig(models.Model):
    url = models.URLField(verbose_name='URL для парсинга')
    params = models.JSONField(default=dict, verbose_name='Параметры запроса')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    schedule = models.ForeignKey(
        PeriodicTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Расписание (Celery)'
    )

    class Meta:
        verbose_name = 'Конфигурация парсера'
        verbose_name_plural = 'Конфигурации парсеров'

class DebugLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    html_content = models.TextField(verbose_name='HTML-контент')
    success = models.BooleanField(verbose_name='Успешно')
    error_message = models.TextField(blank=True, verbose_name='Ошибка')

    class Meta:
        verbose_name = 'Лог парсера'
        verbose_name_plural = 'Логи парсера'
        ordering = ['-created_at']