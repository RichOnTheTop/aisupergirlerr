import os
import io
from typing import Optional
import openai
import logging

logger = logging.getLogger(__name__)

class SpeechToTextService:
    def __init__(self):
        """Инициализация STT сервиса"""
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.enabled = bool(os.getenv("OPENAI_API_KEY"))
        
        if not self.enabled:
            logger.warning("OpenAI API key не найден. STT отключен.")
    
    async def speech_to_text(self, audio_file: io.BytesIO, filename: str = "audio.ogg") -> Optional[str]:
        """Преобразование речи в текст"""
        if not self.enabled:
            return None
            
        try:
            # Подготавливаем файл для Whisper
            audio_file.seek(0)
            audio_file.name = filename
            
            # Используем Whisper для распознавания
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ru"  # Указываем русский язык
            )
            
            return transcript.text.strip()
            
        except Exception as e:
            logger.error(f"Ошибка STT: {e}")
            return None

# Создаем глобальный экземпляр
stt_service = SpeechToTextService()
