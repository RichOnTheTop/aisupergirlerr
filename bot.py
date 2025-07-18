import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.config import load_config
from src.handlers import basic  # voice, payment - добавим позже

async def main():
    """Главная функция запуска бота"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Запуск AI-Girlfriend бота...")
    
    # Загружаем конфигурацию
    config = load_config()
    
    # Создаем бота
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Создаем диспетчер
    dp = Dispatcher()
    
    # Регистрируем
    dp.include_router(basic.router)
    # dp.include_router(voice.router)     # Добавим позже
    # dp.include_router(payment.router)   # Добавим позже
    
    # Пропускаем накопленные апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем поллинг
    logger.info("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
