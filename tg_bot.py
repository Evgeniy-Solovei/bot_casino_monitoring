from aiogram.types import BotCommand
import django_setup
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram_bot.handlers import start, add_domains, delete_domain, list_domains_active, list_domains_no_active
from dotenv import load_dotenv

from aiogram_bot.handlers.add_domains import add_domains_command

load_dotenv()
TOKEN = os.getenv("TOKEN")
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def set_commands():
    commands = [
        BotCommand(command="/start", description="Начать заново"),
        BotCommand(command="/delete_domain", description="Дезактивируем домен (занят, привязан к IP)"),
        BotCommand(command="/add_domains", description="Добавить купленные доменное имена doc.txt"),
        BotCommand(command="/list_domains_active", description="Показать все свободные доменные имена"),
        BotCommand(command="/list_domains_no_active", description="Показать все занятые доменные имена"),
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    logging.info("Бот успешно запущен.")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await set_commands()
        await dp.start_polling(bot)  # Запуск бота
    finally:
        logging.info("Бот остановлен.")


if __name__ == "__main__":
    dp.include_routers(start.router)
    dp.include_routers(add_domains.router)
    dp.include_routers(delete_domain.router)
    dp.include_routers(list_domains_active.router)
    dp.include_routers(list_domains_no_active.router)

    asyncio.run(main())
