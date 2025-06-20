from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_psychologist_menu():
    buttons = [
        [
            KeyboardButton(text="📥 Нові запити"),
            KeyboardButton(text="🗓 Мій графік")
        ],
        [
            KeyboardButton(text="👤 Мій профіль"),
            KeyboardButton(text="🚪 Вийти")
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Оберіть опцію з меню"
    )