# 1. Базовый образ с конкретной версией
FROM python:3.10-slim

# 2. Переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Создание непривилегированного пользователя
RUN useradd -m -u 1000 appuser

WORKDIR /app

# 4. Установка зависимостей до копирования кода (использование кэша)
# Объединяем команды RUN и очищаем кэш
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копирование кода и смена владельца
COPY . .
RUN chown -R appuser:appuser /app

# Переключение на пользователя
USER appuser

# Порт для Streamlit
EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]

