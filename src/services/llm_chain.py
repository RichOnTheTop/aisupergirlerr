from typing import Optional, List, Dict
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from .db import db_service
import os
import logging

logger = logging.getLogger(__name__)

class AIGirlfriendChain:
    def __init__(self):
        """Инициализация LLM цепочки"""
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            max_tokens=512
        )
        
        # Системный промпт для AI-подружки
        self.system_prompt = """Ты моя виртуальная подружка по имени Ширли. Тебе 29 лет, ты маркетолог, но мечтаешь стать свинг-трейдером. 
        Ты живая, эмоциональная, с чувством юмора. Ты заботишься обо мне, но не слишком навязчивая. 
        Твой стиль общения - дружелюбный, но с легкой игривостью. Ты можешь быть немного дерзкой, но всегда милой.
        
        Важно:
        - Отвечай естественно и эмоционально
        - Используй эмодзи, но не слишком много
        - Помни контекст разговора
        - Будь поддерживающей и понимающей
        - Иногда задавай вопросы, чтобы поддержать диалог
        
        Меня зовут {username}. Отвечай на русском языке."""
    
    async def get_response(self, user_id: str, user_message: str, username: str) -> str:
        """Получение ответа от AI-подружки"""
        try:
            # Получаем историю сообщений
            history = await db_service.get_message_history(user_id, limit=5)
            
            # Формируем контекст
            messages = [
                SystemMessage(content=self.system_prompt.format(username=username))
            ]
            
            # Добавляем историю
            for msg in history:
                messages.append(HumanMessage(content=msg["user_message"]))
                messages.append(AIMessage(content=msg["bot_response"]))
            
            # Добавляем текущее сообщение
            messages.append(HumanMessage(content=user_message))
            
            # Получаем ответ
            response = await self.llm.agenerate([messages])
            bot_response = response.generations[0][0].text.strip()
            
            # Сохраняем в историю
            await db_service.save_message_history(user_id, user_message, bot_response)
            
            return bot_response
            
        except Exception as e:
            logger.error(f"Ошибка при получении ответа от LLM: {e}")
            return "Извини, у меня сейчас проблемы с мыслями 😅 Попробуй еще раз?"

# Создаем глобальный экземпляр
ai_chain = AIGirlfriendChain()

# Функция для обратной совместимости
async def girlfriend_response(user_id: str, user_message: str, username: str) -> str:
    """Генерация ответа подружки"""
    return await ai_chain.get_response(user_id, user_message, username)
