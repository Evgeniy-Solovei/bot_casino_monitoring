from aiogram import types, Router
from aiogram.filters import CommandStart

from bot.models import TelegramUser

router = Router()


@router.message(CommandStart())
async def start_command(message: types.Message):
    chat_id = message.chat.id
    # Регистрируем пользователя, если его ещё нет
    await TelegramUser.objects.aget_or_create(chat_id=chat_id)
    help_text = (
        "Привет! Я бот для мониторинга блокировки доменов. Вот что я могу:\n\n"
        "/start - Начать заново\n"
        "/delete_domain - Дезактивируем домен (занят, привязан к IP)\n"
        "/add_domains - Добавить купленные доменное имена doc.txt\n"
        "/list_domains_active - Показать все свободные доменные имена\n"
        "/list_domains_no_active - Показать все занятые доменные имена\n"
    )
    await message.reply(help_text)
