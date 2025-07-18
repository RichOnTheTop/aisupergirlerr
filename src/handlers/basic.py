import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ..services.db import db_service, subscription_valid
from ..services.llm_chain import ai_chain
from ..keyboards.reply import get_main_keyboard

logger = logging.getLogger(__name__)

# Создаем роутер
router = Router(name="basic")

class ConversationStates(StatesGroup):
    """Состояния для диалога"""
    waiting_for_message = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    user_id = str(message.from_user.id)
    username = message.from_user.username or "Дорогой"
    first_name = message.from_user.first_name or "Пользователь"
    
    # Создаем пользователя если его нет
    user_exists = await db_service.get_user(user_id)
    if not user_exists:
        await db_service.create_user(user_id, username, first_name)
    
    welcome_text = f"""Привет, {first_name}! 💕 
    
Я твоя виртуальная подружка Ширли! Мне 29 лет, я маркетолог, но мечтаю стать трейдером 📈

Чтобы начать общение, тебе нужно оплатить подписку. Всего $1 за минуту общения! 💰

Команды:
🔹 /deposit - Оплатить подписку
🔹 /help - Помощь
🔹 /clear - Очистить историю

Готов поболтать? 😊"""
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())
    await state.set_state(ConversationStates.waiting_for_message)

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """🆘 Помощь по боту:

🔹 /start - Начать работу с ботом
🔹 /deposit - Оплатить подписку ($1/мин)
🔹 /clear - Очистить историю диалога
🔹 /help - Это сообщение

💡 Просто напиши мне сообщение, и я отвечу! 
Но сначала не забудь оплатить подписку 😉

❓ Есть вопросы? Напиши @support"""
    
    await message.answer(help_text)

@router.message(Command("clear"))
async def cmd_clear(message: Message):
    """Очистка истории диалога"""
    user_id = str(message.from_user.id)
    
    # Удаляем историю из базы данных
    await db_service.db.message_history.delete_many({"user_id": user_id})
    
    await message.answer("История диалога очищена! 🧹 Можем начать общение заново 😊")

@router.message(StateFilter(ConversationStates.waiting_for_message), F.text & ~F.command)
async def handle_text_message(message: Message, state: FSMContext):
    """Обработка текстовых сообщений"""
    user_id = str(message.from_user.id)
    username = message.from_user.first_name or "Дорогой"
    
    # Проверяем подписку
    if not await subscription_valid(user_id):
        await message.answer(
            "Упс! Похоже, у тебя нет активной подписки 😔\n\n"
            "Чтобы продолжить общение, оплати подписку командой /deposit\n\n"
            "Всего $1 за минуту! 💰",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Отправляем индикатор печати
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        # Получаем ответ от AI
        response = await ai_chain.get_response(user_id, message.text, username)
        
        # Отправляем ответ
        await message.answer(response)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await message.answer("Ой, что-то пошло не так 😅 Попробуй еще раз!")

@router.message(StateFilter(ConversationStates.waiting_for_message))
async def handle_other_content(message: Message):
    """Обработка других типов контента"""
    await message.answer("Пока я умею только с текстом общаться 😊 Напиши мне что-нибудь!")
