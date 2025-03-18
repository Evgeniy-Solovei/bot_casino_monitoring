from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.models import Domain

router = Router()

# Состояния для FSM (Finite State Machine)
class DeleteDomainState(StatesGroup):
    waiting_for_domain = State()  # Состояние ожидания ввода домена

# Обработчик команды /delete_domain
@router.message(Command("delete_domain"))
async def delete_domain_command(message: Message, state: FSMContext):
    # Запрашиваем у пользователя доменное имя
    await message.answer("Введите доменное имя для деактивации:")
    # Устанавливаем состояние ожидания ввода домена
    await state.set_state(DeleteDomainState.waiting_for_domain)

# Обработчик ввода доменного имени
@router.message(DeleteDomainState.waiting_for_domain, F.text)
async def process_domain_name(message: Message, state: FSMContext):
    domain_name = message.text.strip().lower()  # Очищаем ввод и приводим к нижнему регистру

    # Ищем домен в базе данных
    domain = await Domain.objects.filter(name=domain_name).afirst()

    if domain:
        # Деактивируем домен (устанавливаем is_active = False)
        domain.is_active = False
        await domain.asave()  # Асинхронное сохранение изменений
        await message.answer(f"✅ Домен {domain_name} успешно деактивирован.")
    else:
        await message.answer(f"⚠️ Домен {domain_name} не найден в базе данных.")

    # Сбрасываем состояние
    await state.clear()

