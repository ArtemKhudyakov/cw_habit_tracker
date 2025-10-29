FROM python:3.13-slim

ARG SECRET_KEY
ENV SECRET_KEY=$SECRET_KEY

WORKDIR /app

# Копирование зависимостей
COPY pyproject.toml poetry.lock ./

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry и зависимостей
RUN pip install poetry
RUN poetry config virtualenvs.create false

# Установка зависимостей
RUN poetry install --no-interaction --no-ansi --no-root

# Копирование проекта
COPY . .

# Собираем статические файлы
#RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", " \
  echo '🚀 Starting cw_habbit_tracker aplication...' && \
  echo '⏳ Waiting for PostgreSQL...' && \
  while ! nc -z db 5432; do sleep 1; done && \
  echo '✅ PostgreSQL started' && \
  echo '⏳ Waiting for Redis...' && \
  while ! nc -z redis 6379; do sleep 1; done && \
  echo '✅ Redis started' && \
  echo '📦 Running migrations...' && \
  python manage.py migrate && \
  echo '📁 Collecting static files...' && \
  python manage.py collectstatic --noinput && \
  echo '👤 Creating superuser...' && \
  python manage.py create_superuser || echo 'ℹ️ Superuser creation skipped' && \
  echo '🎯 Starting Gunicorn server...' && \
  gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile - \
"]