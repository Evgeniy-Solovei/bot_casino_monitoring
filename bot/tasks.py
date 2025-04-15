import requests
from celery import shared_task
from django.utils import timezone
from django.utils.timezone import now
from .models import Domain
from .views import send_telegram_message


API_URL = "https://reestr.rublacklist.net/api/v3/domains/"


def send_domain_status_to_api(domain_name, status="Не Активен"):
    url = "https://api.gang-soft.com/api/take_bot_data/"
    payload = {
        "current_domain": domain_name,
        "domain_mask": domain_name,
        "status": status
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10, verify=False)  # verify=False — отключаем SSL
        if response.status_code == 200:
            print(f"✔️ Домен {domain_name} успешно отправлен на сервер.")
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
    except Exception as e:
        print(f"⚠️ Ошибка при отправке данных домена {domain_name}: {e}")


@shared_task
def check_domain_availability():
    """Тестовая проверка доступности доменов (HTTP 200), с отправкой всех результатов."""
    print(">>> Запуск тестовой проверки доменов")
    domains = Domain.objects.filter(is_active=True)
    print(f"Найдено активных доменов: {domains.count()}")

    result_messages = []  # Список для хранения всех сообщений

    for domain in domains:
        try:
            response = requests.get(f"http://{domain.name}", timeout=5)
            accessible = response.status_code == 200
        except requests.exceptions.RequestException:
            accessible = False

        # Логика для теста - создаем строку для каждого домена
        status_text = "✅ Доступен" if accessible else "❌ Недоступен"
        result_messages.append(f"{status_text}: {domain.name}")

        # Обновляем статус в БД (если отличается)
        if accessible != domain.is_accessible:
            print(f"Обновление доступности домена {domain.name} с {domain.is_accessible} на {accessible}")
            domain.is_accessible = accessible
            domain.last_checked = timezone.localtime()
            domain.save()

    # Отправляем все результаты в одном сообщении
    if result_messages:
        send_telegram_message("\n".join(result_messages))


@shared_task
def check_api_blocked_domains():
    """Тестовая проверка доменов через API (реестр заблокированных), с отправкой всех результатов."""
    response = requests.get(API_URL, timeout=10)
    if response.status_code != 200:
        send_telegram_message("❌ Ошибка при получении данных из API блокировок.")
        return
    # Очистка доменов от лишних кавычек
    blocked_domains = set(domain.strip('\"') for domain in response.json())  # Убираем кавычки с доменов
    domains = Domain.objects.filter(is_active=True)
    result_messages = []  # Список для хранения всех сообщений
    for domain in domains:
        is_blocked = domain.name in blocked_domains
        # Логика для теста - создаем строку для каждого домена
        status_text = "🚫 В реестре" if is_blocked else "✅ Не в реестре"
        result_messages.append(f"{status_text}: {domain.name}")
        # Обновляем статус в БД (если отличается)
        if is_blocked != domain.is_blocked_api:
            print(f"Обновление доступности домена {domain.name} с {domain.is_accessible} на {is_blocked}")
            domain.is_blocked_api = is_blocked
            domain.last_checked = timezone.localtime()
            domain.save()
            if is_blocked:
                send_domain_status_to_api(domain.name, status="Заблокирован")
    # Отправляем все результаты в одном сообщении
    if result_messages:
        send_telegram_message("\n".join(result_messages))
