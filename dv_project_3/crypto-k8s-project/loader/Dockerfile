FROM python:3.9-slim
WORKDIR /app
# Устанавливаем зависимости для psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip install pandas psycopg2-binary

# Копируем скрипт и ПАПКУ с данными
COPY loader.py .
COPY raw_data/ ./raw_data/ 

CMD ["python", "loader.py"]