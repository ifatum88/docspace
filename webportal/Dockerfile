# Используем официальный python-образ
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект внутрь контейнера
COPY . .

# Указываем порт, на котором будет работать приложение
EXPOSE 8000

# Команда запуска
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8888", "run:app"]