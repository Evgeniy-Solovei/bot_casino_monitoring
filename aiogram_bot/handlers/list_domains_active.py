from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.models import Domain

router = Router()

# Обработчик команды /list_domains_active
@router.message(Command("list_domains_active"))
async def list_active_domains(message: Message):
    # Асинхронно загружаем активные домены из базы данных
    active_domains = [domain async for domain in Domain.objects.filter(is_active=True).aiterator()]

    if active_domains:
        # Формируем список доменов (синхронная операция)
        domains_list = "\n".join([domain.name for domain in active_domains])
        await message.answer(f"✅ Список активных доменов:\n{domains_list}")
    else:
        await message.answer("⚠️ Активных доменов не найдено.")