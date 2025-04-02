FROM python:3.9-slim

# Установка системных зависимостей с явным указанием пакета netcat-traditional
RUN apt-get update && apt-get install -y \
    iputils-ping \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем структуру проекта
COPY fake_reviews_detector/ ./fake_reviews_detector/
COPY api/ ./api/
COPY reviews/ ./reviews/
COPY manage.py .

# Настройка путей
ENV PYTHONPATH="${PYTHONPATH}:/app:/app/fake_reviews_detector"

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]