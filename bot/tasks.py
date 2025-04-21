import os
import random
import string
from xml.etree import ElementTree as ET
import requests
from celery import shared_task
from django.utils import timezone
from dotenv import load_dotenv
from .models import Domain
from .views import send_telegram_message


load_dotenv()

API_URL = "https://reestr.rublacklist.net/api/v3/domains/"
API_USER = os.getenv("API_USER")
API_KEY = os.getenv("API_KEY")
USERNAME = os.getenv("USERNAME")
CLIENT_IP = os.getenv("CLIENT_IP")


def send_domain_status_to_api(domain_name, domain_mask, status, create_domain, domain_mask_2, status_2):
    """Отправка статуса домена на сервер Gang-Soft."""
    url = "https://api.gang-soft.com/api/take_bot_data/"
    payload = {
        "current_domain": domain_name,
        "domain_mask": domain_mask,
        "status": status,
        'current_domain_2': create_domain,
        'domain_mask_2': domain_mask_2,
        'status_2': status_2
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




def generate_random_suffix(length=3):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def get_tld_price(tld):
    params = {
        'ApiUser': API_USER,
        'ApiKey': API_KEY,
        'UserName': USERNAME,
        'Command': 'namecheap.users.getPricing',
        'ClientIp': CLIENT_IP,
        'ProductType': 'DOMAIN',
        'ProductCategory': 'REGISTER',
        'ProductName': tld
    }
    try:
        response = requests.get('https://api.namecheap.com/xml.response', params=params, timeout=15)
        root = ET.fromstring(response.content)
        price_el = root.find('.//{http://api.namecheap.com/xml.response}Price')
        if price_el is not None:
            return float(price_el.attrib.get('Price', '999'))
    except Exception:
        pass
    return 999

def check_domain_available(domain_name):
    params = {
        'ApiUser': API_USER,
        'ApiKey': API_KEY,
        'UserName': USERNAME,
        'Command': 'namecheap.domains.check',
        'ClientIp': CLIENT_IP,
        'DomainList': domain_name
    }
    try:
        response = requests.get('https://api.namecheap.com/xml.response', params=params, timeout=15)
        root = ET.fromstring(response.content)
        result = root.find('.//{http://api.namecheap.com/xml.response}DomainCheckResult')
        if result is not None:
            return result.attrib.get('Available') == 'true'
    except Exception:
        pass
    return False


def find_cheap_domain(base_name, max_price=4.0, attempts=30):
    """Поиск доменного имени для покупки"""
    zones = ['com', 'net', 'org', 'xyz', 'online', 'site', 'store', 'tech', 'fun']
    for _ in range(attempts):
        suffix = generate_random_suffix()
        zone = random.choice(zones)
        domain = f"{base_name}-{suffix}.{zone}"
        price = get_tld_price(zone)
        if price <= max_price and check_domain_available(domain):
            print(f"✅ Домен найден: {domain} за ${price:.2f}")
            return domain
        else:
            print(f"⏩ {domain} — недоступен или дорогой (${price:.2f})")
    print("❌ Ничего не найдено")
    return None


def purchase_domain(domain_name):
    """Регистрация домена через API Namecheap"""
    params = {
        'ApiUser': API_USER,
        'ApiKey': API_KEY,
        'UserName': USERNAME,
        'Command': 'namecheap.domains.create',
        'ClientIp': CLIENT_IP,
        'DomainName': domain_name,
        'Years': 1,
        'RegistrantFirstName': 'Ivan',
        'RegistrantLastName': 'Ivanov',
        'RegistrantAddress1': 'Lenina 1',
        'RegistrantCity': 'Minsk',
        'RegistrantStateProvince': 'Minsk',
        'RegistrantPostalCode': '111',
        'RegistrantCountry': 'BY',
        'RegistrantPhone': '+375.291234567',
        'RegistrantEmailAddress': 'kasyadounar@gmail.com',
        'RegistrantOrganizationName': 'Company Inc.',
        'RegistrantJobTitle': 'CEO',
        'TechFirstName': 'Ivan',
        'TechLastName': 'Ivanov',
        'TechAddress1': 'Lenina 1',
        'TechCity': 'Minsk',
        'TechStateProvince': 'Minsk',
        'TechPostalCode': '111',
        'TechCountry': 'BY',
        'TechPhone': '+375.291234567',
        'TechEmailAddress': 'tech@example.com',
        'TechOrganizationName': 'TechCorp',
        'TechJobTitle': 'CTO',
        'AdminFirstName': 'Ivan',
        'AdminLastName': 'Ivanov',
        'AdminAddress1': 'Lenina 1',
        'AdminCity': 'Minsk',
        'AdminStateProvince': 'Minsk',
        'AdminPostalCode': '111',
        'AdminCountry': 'BY',
        'AdminPhone': '+375.291234567',
        'AdminEmailAddress': 'admin@example.com',
        'AdminOrganizationName': 'AdminCorp',
        'AdminJobTitle': 'Administrator',
        'AuxBillingFirstName': 'John',
        'AuxBillingLastName': 'Doe',
        'AuxBillingAddress1': 'Main St 123',
        'AuxBillingCity': 'Minsk',
        'AuxBillingStateProvince': 'Minsk',
        'AuxBillingPostalCode': '222',
        'AuxBillingCountry': 'BY',
        'AuxBillingPhone': '+375.291234567',
        'AuxBillingEmailAddress': 'billing@example.com',
        'AddFreeWhoisguard': 'no',
        'WGEnabled': 'no',
        'IsPremiumDomain': 'false',
        'PremiumPrice': '0',
        'EapFee': '0',
        'GenerateAdminOrderRefId': 'False',
    }

    try:
        response = requests.get('https://api.namecheap.com/xml.response', params=params, timeout=60)
        print(f"📨 Ответ Namecheap (raw):\n{response.text}")  # ← главное

        root = ET.fromstring(response.content)

        # 🔥 Вытаскиваем текст ошибки
        error_el = root.find('.//{http://api.namecheap.com/xml.response}Error')
        if error_el is not None:
            print(f"❌ Ошибка от Namecheap: {error_el.text}")

        # Продолжаем разбор
        result = root.find('.//{http://api.namecheap.com/xml.response}DomainCreateResult')
        if result is not None:
            print("⚙️ Нашёл элемент DomainCreateResult")
            print(f"➡️ Атрибуты: {result.attrib}")
            if result.attrib.get('Registered') == 'true':
                print(f"✅ Домен {domain_name} успешно зарегистрирован.")
                return True
            else:
                print(f"❌ Домен не зарегистрирован. Причина: {result.attrib}")
        else:
            print("❌ Не найден элемент DomainCreateResult")

    except Exception as e:
        print(f"❌ Ошибка при регистрации домена {domain_name}: {e}")

    return False


def create_cloudflare_zone(domain_name: str) -> list[str] | None:
    """Создание зоны в Cloudflare и получение NS"""
    headers = {
        "X-Auth-Email": "odin.vin@yandex.ru",
        "X-Auth-Key": "625a435d54464faa61c5fdf7360adade9e828",
        "Content-Type": "application/json",
    }
    data = {
        "name": domain_name,
        "jump_start": True,
    }

    try:
        response = requests.post(
            "https://api.cloudflare.com/client/v4/zones",
            json=data,
            headers=headers,
            timeout=15
        )
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("success"):
                nameservers = res_json["result"].get("name_servers")
                print(f"✅ Зона {domain_name} создана. NS: {nameservers}")
                return nameservers
            else:
                print(f"⚠️ Не удалось создать зону: {res_json}")
        else:
            print(f"❌ Ошибка при создании зоны: {response.status_code} — {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при запросе к Cloudflare: {e}")
    return None


def set_nameservers(domain_name, ns1, ns2):
    """Установка NS для домена через API Namecheap"""
    sld, tld = domain_name.split('.')  # разделяем домен
    params = {
        'ApiUser': API_USER,
        'ApiKey': API_KEY,
        'UserName': USERNAME,
        'Command': 'namecheap.domains.dns.setCustom',
        'ClientIp': CLIENT_IP,
        'SLD': sld,
        'TLD': tld,
        'Nameservers': f"{ns1},{ns2}"
    }

    print(f"📤 Отправляем запрос на смену NS для {domain_name}: {ns1}, {ns2}")
    print(f"🔧 Параметры: {params}")

    try:
        response = requests.get('https://api.namecheap.com/xml.response', params=params, timeout=15)
        print(f"📨 Ответ от Namecheap (смена NS):\n{response.text}")

        root = ET.fromstring(response.content)
        result = root.find('.//{http://api.namecheap.com/xml.response}DomainDNSSetCustomResult')
        if result is not None:
            if result.attrib.get('Updated') == 'true':
                print(f"✅ NS для {domain_name} успешно обновлены.")
                return True
            else:
                print(f"❌ NS НЕ обновлены: {result.attrib}")
        else:
            print("❌ Элемент DomainDNSSetCustomResult не найден")
    except Exception as e:
        print(f"❌ Ошибка при установке NS: {e}")
    return False


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
        status_text = "✅ Доступен в сети интернет" if accessible else "❌ Недоступен в сети интернет"
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
        status_text = "🚫 Заблокирован в РКН" if is_blocked else "✅ Доступен в РКН"
        result_messages.append(f"{status_text}: {domain.name}")
        # Обновляем статус в БД (если отличается)
        if is_blocked != domain.is_blocked_api:
            print(f"Обновление доступности домена {domain.name} с {domain.is_accessible} на {is_blocked}")
            domain.is_blocked_api = is_blocked
            domain.last_checked = timezone.localtime()
            domain.save()
    # Отправляем все результаты в одном сообщении
    if result_messages:
        send_telegram_message("\n".join(result_messages))




@shared_task
def check_api_blocked_domains_pay_now_domain():
    """Тестовая проверка доменов через API (реестр заблокированных), с отправкой всех результатов."""
    response = requests.get(API_URL, timeout=10)
    if response.status_code != 200:
        send_telegram_message("❌ Ошибка при получении данных из API блокировок.")
        return
    # Очистка доменов от лишних кавычек
    blocked_domains = set(domain.strip('\"') for domain in response.json())  # Убираем кавычки с доменов
    domains = Domain.objects.filter(is_active=True, is_blocked_api=True, pay_domains=False)
    result_messages = []  # Список для хранения всех сообщений
    for domain in domains:
        is_blocked = domain.name in blocked_domains
        # Определяем маску домена
        domain_mask = "1win" if "1win" in domain.name.lower() else "pokerdom" if "pokerdom" in domain.name.lower() else domain.name
        # Логика для теста - создаем строку для каждого домена
        status_text = "🚫 Заблокирован в РКН" if is_blocked else "✅ Доступен в РКН"
        result_messages.append(f"{status_text}: {domain.name}")
        # Обновляем статус в БД (если отличается)
        if is_blocked != domain.is_blocked_api:
            print(f"Обновление доступности домена {domain.name} с {domain.is_accessible} на {is_blocked}")
            domain.is_blocked_api = is_blocked
            domain.last_checked = timezone.localtime()
            domain.pay_domains = True
            domain.save()
            #Поиск доменного имени для покупки
            create_domain = find_cheap_domain(base_name=domain_mask)
            #Регистрация домена через API Namecheap
            purchase_domain(domain_name=create_domain)
            #Создание зоны в Cloudflare и получение NS
            nameservers = create_cloudflare_zone(domain_name=create_domain)
            if nameservers:
                #Установка NS для домена через API Namecheap
                set_nameservers(create_domain, nameservers[0], nameservers[1])
            if is_blocked:
                #Отправка статуса домена на сервер Gang-Soft
                send_domain_status_to_api(domain_name=domain.name, domain_mask=domain_mask, status="Заблокирован",
                                          create_domain=create_domain, domain_mask_2=domain_mask, status_2="Не Активен")

    # Отправляем все результаты в одном сообщении
    if result_messages:
        send_telegram_message("\n".join(result_messages))



def test_check_one_domain(domain_name):
    """Ручная проверка одного домена (как в проде, с покупкой нового, если заблокирован)."""
    response = requests.get(API_URL, timeout=10)
    if response.status_code != 200:
        send_telegram_message("❌ Ошибка при получении данных из API блокировок.")
        return

    blocked_domains = set(domain.strip('\"') for domain in response.json())

    try:
        domain = Domain.objects.get(name=domain_name)
    except Domain.DoesNotExist:
        print(f"❌ Домен {domain_name} не найден в БД")
        return

    is_blocked = domain.name in blocked_domains
    domain_mask = (
        "1win" if "1win" in domain.name.lower()
        else "pokerdom" if "pokerdom" in domain.name.lower()
        else domain.name
    )

    status_text = "🚫 Заблокирован в РКН" if is_blocked else "✅ Доступен в РКН"
    print(f"{status_text}: {domain.name}")

    if is_blocked != domain.is_blocked_api:
        print(f"Обновление доступности домена {domain.name} с {domain.is_blocked_api} на {is_blocked}")
        domain.is_blocked_api = is_blocked
        domain.last_checked = timezone.localtime()
        domain.save()

        create_domain = find_cheap_domain(base_name=domain_mask)
        print(create_domain)
        a = purchase_domain(domain_name=create_domain)
        print(a)
        nameservers = create_cloudflare_zone(domain_name=create_domain)
        print("nameservers:", nameservers)
        if nameservers:
            set_nameservers(create_domain, nameservers[0], nameservers[1])
        if is_blocked:
            send_domain_status_to_api(
                domain_name=domain.name,
                domain_mask=domain_mask,
                status="Заблокирован",
                create_domain=create_domain,
                domain_mask_2=domain_mask,
                status_2="Активен")
    send_telegram_message(f"{status_text}: {domain.name}")
