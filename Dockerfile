# Используем базовый образ Python 3.12 с поддержкой Chrome и chromedriver
FROM python:3.12

# Команда для вывода логов в консоле
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочий каталог
WORKDIR /bot_core

# Устанавливаем часовой пояс Europe/Moscow
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем проект
COPY . .

# Открываем порт
EXPOSE 8000

# Запускаем миграции, сервер и бота одновременно
CMD ["sh", "-c", "python manage.py migrate && uvicorn bot_core.asgi:application --host 0.0.0.0 --port 8000 & python tg_bot.py"]
