# Используем базовый образ Python
FROM python:3.11-slim-buster

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY . .

# Устанавливаем переменные окружения
ENV DATABASE_URL=postgresql://postgres:postgres@db:5435/postgres

# Запускаем приложение Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]