# backend/Dockerfile

# Базовый образ Python 3.11 (минималистичная версия)
FROM python:3.11-slim

# Устанавливаем рабочую папку внутри контейнера
WORKDIR /app

# Отключаем кэширование байт-кода и буферизацию вывода Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установка системных зависимостей, необходимых для сборки библиотек
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Для работы psycopg2 (PostgreSQL adapter)
    libpq-dev \
    # Для поддержки изображений через Pillow
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    # Дополнительные утилиты (например, для локализации)
    gettext \
    # Очистка системы после установки
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем файл со списком Python-зависимостей
COPY backend/requirements.txt .

# Устанавливаем зависимости Python без кэша, чтобы уменьшить размер образа
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код бэкенд-приложения в рабочую директорию
COPY backend/ /app/

# Указываем порт, который будет использоваться приложением
EXPOSE 8000

# Финальная команда запуска определена в docker-compose.yml
# Она включает миграции, сбор статики и запуск Gunicorn
