from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.models import Domain

router = Router()

# Обработчик команды /list_domains_no_active
@router.message(Command("list_domains_no_active"))
async def list_inactive_domains(message: Message):
    # Асинхронно загружаем неактивные домены из базы данных
    inactive_domains = [domain async for domain in Domain.objects.filter(is_active=False).aiterator()]

    if inactive_domains:
        # Формируем список доменов (синхронная операция)
        domains_list = "\n".join([domain.name for domain in inactive_domains])
        await message.answer(f"✅ Список неактивных доменов:\n{domains_list}")
    else:
        await message.answer("⚠️ Неактивных доменов не найдено.")
