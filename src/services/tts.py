import os
import io
from typing import Optional
from elevenlabs import generate, set_api_key, voices
import logging

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        """Инициализация TTS сервиса"""
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if api_key:
            set_api_key(api_key)
            self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel по умолчанию
            self.enabled = True
        else:
            self.enabled = False
            logger.warning("ElevenLabs API key не найден. TTS отключен.")
    
    async def text_to_speech(self, text: str) -> Optional[io.BytesIO]:
        """Преобразование текста в речь"""
        if not self.enabled:
            return None
            
        try:
            # Генерируем аудио
            audio = generate(
                text=text,
                voice=self.voice_id,
                model="eleven_monolingual_v1"
            )
            
            # Возвращаем как BytesIO объект
            audio_buffer = io.BytesIO(audio)
            audio_buffer.seek(0)
            return audio_buffer
            
        except Exception as e:
            logger.error(f"Ошибка TTS: {e}")
            return None
    
    async def get_available_voices(self) -> list:
        """Получение списка доступных голосов"""
        if not self.enabled:
            return []
        
        try:
            return voices()
        except Exception as e:
            logger.error(f"Ошибка получения голосов: {e}")
            return []

# Создаем глобальный экземпляр
tts_service = TTSService()
