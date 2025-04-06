FROM python:3.9-slim

# Установка системных зависимостей с явным указанием пакета netcat-traditional
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        iputils-ping \
        netcat-traditional \
        curl \
        libxml2-dev \
        libxslt1-dev \
        gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем проект и модель
COPY models/ ./models/
COPY fake_reviews_detector/ ./fake_reviews_detector/
COPY api/ ./api/
COPY reviews/ ./reviews/
COPY manage.py .

# Настройка путей
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Healthcheck с использованием curl
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl --fail http://localhost:8000/healthcheck/ || exit 1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]