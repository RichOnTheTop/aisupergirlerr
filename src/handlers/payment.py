import logging
from aiogram import Router
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice
from aiogram.filters import Command

from ..services.db import db_service

logger = logging.getLogger(__name__)

# Создаем роутер (пока не регистрируем)
router = Router(name="payment")

@router.message(Command("deposit"))
async def cmd_deposit(message: Message):
    """Обработчик команды оплаты"""
    # Временно отключено
    await message.answer(
        "💰 Система оплаты временно отключена!\n\n"
        "В данный момент бот работает в тестовом режиме.\n"
        "Скоро добавим Telegram Stars и другие способы оплаты! ⭐"
    )
    return
    
    # Код ниже будет активирован позже
    user_id = str(message.from_user.id)
    
    # Создаем инвойс на 1 минуту общения ($1)
    prices = [LabeledPrice(label="1 минута общения", amount=100)]  # $1.00
    
    await message.answer_invoice(
        title="Подписка на AI-подружку",
        description="Оплата за 1 минуту общения с виртуальной подружкой",
        payload=f"subscription_{user_id}",
        provider_token="",  # Токен платежного провайдера
        currency="USD",
        prices=prices,
        start_parameter="subscription",
        photo_url="https://example.com/bot_payment_image.jpg",
        photo_size=512,
        photo_width=512,
        photo_height=512
    )

@router.pre_checkout_query()
async def pre_checkout_handler(query: PreCheckoutQuery):
    """Обработчик предварительной проверки платежа"""
    await query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    """Обработчик успешного платежа"""
    user_id = str(message.from_user.id)
    
    # Активируем подписку на 1 минуту
    await db_service.update_subscription(user_id, 1)
    
    await message.answer(
        "🎉 Платеж успешно обработан!\n\n"
        "Твоя подписка активирована на 1 минуту.\n"
        "Теперь можешь общаться с AI-подружкой! 💕"
    )
