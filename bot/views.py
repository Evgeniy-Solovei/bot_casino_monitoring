import os

import httpx
from django.shortcuts import render
import requests
from dotenv import load_dotenv

from bot.models import TelegramUser

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TOKEN")


def send_telegram_message(text: str):
    """Синхронная отправка сообщений через Telegram API."""
    print(f"Попытка отправить сообщение: {text}")
    for user in TelegramUser.objects.all():
        print(f"Отправка пользователю {user.chat_id}")
        payload = {
            "chat_id": user.chat_id,
            "text": text
        }
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json=payload,
                timeout=5
            )
            # Дополнительные проверки ответа при необходимости
            if response.status_code != 200:
                print(f"Ошибка отправки: {response.text}")
        except requests.exceptions.RequestError as e:
            print(f"Ошибка запроса: {e}")
            continue
