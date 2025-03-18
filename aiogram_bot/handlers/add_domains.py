from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from django.utils.timezone import now
import re
from bot.tasks import check_domain_availability, check_api_blocked_domains
from bot.models import Domain
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


router = Router()
DOMAIN_REGEX = re.compile(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Состояния для FSM
class AddDomainsState(StatesGroup):
    waiting_for_domains = State()  # Состояние ожидания ввода доменов или файла

# Обработчик команды /add_domains
@router.message(Command("add_domains"))
async def add_domains_command(message: Message, state: FSMContext):
    # Запрашиваем у пользователя ввод доменов или отправку файла
    await message.answer(
        "Введите доменные имена через пробел или отправьте файл с доменами (каждый на новой строке)."
    )
    # Устанавливаем состояние ожидания
    await state.set_state(AddDomainsState.waiting_for_domains)

# Обработчик ввода доменов или файла
@router.message(AddDomainsState.waiting_for_domains, F.text | F.document)
async def process_domains_input(message: Message, state: FSMContext):
    domains_to_add = set()

    # Если пользователь ввел текст
    if message.text:
        # Извлекаем домены из текста сообщения
        domains_to_add = {d.strip().lower() for d in message.text.split() if DOMAIN_REGEX.match(d.strip())}

    # Если пользователь отправил файл
    elif message.document:
        file = await message.bot.get_file(message.document.file_id)
        file_content = await message.bot.download_file(file.file_path)
        # Читаем домены из файла
        domains_to_add = {line.strip().lower() for line in file_content.read().decode("utf-8").splitlines() if DOMAIN_REGEX.match(line.strip())}

    # Если домены не найдены
    if not domains_to_add:
        await message.answer("⚠️ Не найдено корректных доменных имен.")
        await state.clear()  # Сбрасываем состояние
        return

    # Ищем уже существующие домены (асинхронно)
    existing_domains = set()
    async for domain in Domain.objects.filter(name__in=domains_to_add).aiterator():
        existing_domains.add(domain.name)

    new_domains = domains_to_add - existing_domains

    # Добавляем только новые домены
    if new_domains:
        # Используем abulk_create для асинхронного добавления доменов
        await Domain.objects.abulk_create([Domain(name=d, last_checked=now()) for d in new_domains])
        await message.answer(f"✅ Добавлены домены:\n" + "\n".join(new_domains))
    else:
        await message.answer("⚠️ Все домены уже есть в БД.")

    # Запускаем асинхронные таски на проверку доступности и блокировки
    check_domain_availability.delay()
    check_api_blocked_domains.delay()
    await message.answer("🔄 Запущена проверка доступности и блокировки новых доменов...")

    # Сбрасываем состояние
    await state.clear()
