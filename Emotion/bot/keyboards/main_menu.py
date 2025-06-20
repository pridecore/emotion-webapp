from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    buttons = [
        [KeyboardButton(text="🧠 Записатись на консультацію")],
        [KeyboardButton(text="✨ Афірмація дня"), KeyboardButton(text="📖 Мої бронювання")],
        [KeyboardButton(text="👤 Мій профіль"), KeyboardButton(text="ℹ️ Про бота")],
        [KeyboardButton(text="📤 Поділитися ботом"), KeyboardButton(text="✉️ Зворотний зв’язок")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Оберіть дію…"
    )

# Меню психолога
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