import requests
from celery import shared_task
from django.utils import timezone
from django.utils.timezone import now
from .models import Domain
from .views import send_telegram_message


API_URL = "https://reestr.rublacklist.net/api/v3/domains/"


# @shared_task
# def check_domain_availability():
#     """Проверка доступности доменов (HTTP 200)."""
#     print(">>> Запуск проверки доменов")
#     domains = Domain.objects.filter(is_active=True)
#     print(f"Найдено активных доменов: {domains.count()}")
#     for domain in domains:
#         try:
#             response = requests.get(f"http://{domain.name}", timeout=5)
#             accessible = response.status_code == 200
#         except requests.exceptions.RequestException:
#             accessible = False
#         if accessible != domain.is_accessible:  # Состояние изменилось
#             domain.is_accessible = accessible
#             domain.last_checked = timezone.localtime()
#             domain.save()
#             if accessible:
#                 send_telegram_message(f"✅ Домен {domain.name} снова доступен.")
#             else:
#                 send_telegram_message(f"⚠️ Домен {domain.name} стал недоступен.")
#
#
# @shared_task
# def check_api_blocked_domains():
#     """Проверка доменов через API (реестр заблокированных)."""
#     response = requests.get(API_URL, timeout=10)
#     if response.status_code != 200:
#         send_telegram_message("❌ Ошибка при получении данных из API блокировок.")
#         return
#     blocked_domains = set(response.json())
#     domains = Domain.objects.filter(is_active=True)
#     for domain in domains:
#         is_blocked = domain.name in blocked_domains
#         if is_blocked != domain.is_blocked_api:
#             domain.is_blocked_api = is_blocked
#             domain.last_checked = now()
#             domain.save()
#             if is_blocked:
#                 send_telegram_message(f"🚫 Домен {domain.name} добавлен в реестр блокировок.")
#             else:
#                 send_telegram_message(f"✅ Домен {domain.name} удалён из реестра блокировок.")


@shared_task
def check_domain_availability():
    """Тестовая проверка доступности доменов (HTTP 200), с отправкой всех результатов."""
    print(">>> Запуск тестовой проверки доменов")
    domains = Domain.objects.filter(is_active=True)
    print(f"Найдено активных доменов: {domains.count()}")

    for domain in domains:
        try:
            response = requests.get(f"http://{domain.name}", timeout=5)
            accessible = response.status_code == 200
        except requests.exceptions.RequestException:
            accessible = False

        # Логика для теста - отправляем инфу о каждом домене
        status_text = "✅ Доступен" if accessible else "❌ Недоступен"
        send_telegram_message(f"{status_text}: {domain.name}")

        # Обновляем статус в БД (если отличается)
        if accessible != domain.is_accessible:
            domain.is_accessible = accessible
            domain.last_checked = timezone.localtime()
            domain.save()


@shared_task
def check_api_blocked_domains():
    """Тестовая проверка доменов через API (реестр заблокированных), с отправкой всех результатов."""
    response = requests.get(API_URL, timeout=10)
    if response.status_code != 200:
        send_telegram_message("❌ Ошибка при получении данных из API блокировок.")
        return

    blocked_domains = set(response.json())
    domains = Domain.objects.filter(is_active=True)

    for domain in domains:
        is_blocked = domain.name in blocked_domains

        # Логика для теста - отправляем инфу о каждом домене
        status_text = "🚫 В реестре" if is_blocked else "✅ Не в реестре"
        send_telegram_message(f"{status_text}: {domain.name}")

        # Обновляем статус в БД (если отличается)
        if is_blocked != domain.is_blocked_api:
            domain.is_blocked_api = is_blocked
            domain.last_checked = timezone.localtime()
            domain.save()
