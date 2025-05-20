# Dockerfile

FROM python:3.11-slim

# Установка зависимостей
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Собираем статику (если понадобится)
RUN python manage.py collectstatic --noinput

# Запускаем Gunicorn
CMD ["gunicorn", "korean_shop.wsgi:application", "--bind", "0.0.0.0:8000"]
