from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="💰 Оплатить подписку"),
                KeyboardButton(text="ℹ️ Помощь")
            ],
            [
                KeyboardButton(text="🧹 Очистить историю"),
                KeyboardButton(text="👋 Начать заново")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard
