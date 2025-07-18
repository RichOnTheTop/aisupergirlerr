import logging
import io
from aiogram import Router, F
from aiogram.types import Message, Voice
from aiogram.filters import StateFilter

from ..services.db import subscription_valid
from ..services.llm_chain import ai_chain
from ..services.tts import tts_service
from ..services.speech_to_text import stt_service
from .basic import ConversationStates

logger = logging.getLogger(__name__)

# Создаем роутер (пока не регистрируем)
router = Router(name="voice")

@router.message(StateFilter(ConversationStates.waiting_for_message), F.voice)
async def handle_voice_message(message: Message):
    """Обработка голосовых сообщений"""
    user_id = str(message.from_user.id)
    username = message.from_user.first_name or "Дорогой"
    
    # Проверяем подписку
    if not await subscription_valid(user_id):
        await message.answer("Для использования голосовых сообщений нужна подписка! /deposit")
        return
    
    # Временно отключено
    await message.answer("Голосовые сообщения временно отключены 🔇\nНапиши мне текстом! 😊")
    return
    
    # Код ниже будет активирован позже
    try:
        # Скачиваем голосовое сообщение
        voice: Voice = message.voice
        file_info = await message.bot.get_file(voice.file_id)
        file_data = await message.bot.download_file(file_info.file_path)
        
        # Преобразуем речь в текст
        audio_buffer = io.BytesIO(file_data.getvalue())
        user_text = await stt_service.speech_to_text(audio_buffer, "voice.ogg")
        
        if not user_text:
            await message.answer("Не удалось распознать речь 😕 Попробуй еще раз!")
            return
        
        # Отправляем индикатор печати
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        
        # Получаем ответ от AI
        response = await ai_chain.get_response(user_id, user_text, username)
        
        # Генерируем голосовой ответ
        voice_response = await tts_service.text_to_speech(response)
        
        if voice_response:
            # Отправляем голосовое сообщение
            await message.answer_voice(voice_response)
        else:
            # Отправляем текст если TTS не работает
            await message.answer(response)
            
    except Exception as e:
        logger.error(f"Ошибка при обработке голосового сообщения: {e}")
        await message.answer("Произошла ошибка при обработке голосового сообщения 😔")
