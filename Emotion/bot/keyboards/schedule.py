from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Вибір днів тижня
def get_days_keyboard():
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
    buttons = [
        [InlineKeyboardButton(text=day, callback_data=f"day_{day}")] for day in days
    ]
    buttons.append([InlineKeyboardButton(text="✅ Готово", callback_data="days_done")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Вибір години (для старту або завершення робочого дня)
def get_time_keyboard(prefix: str):
    times = [f"{h:02}:00" for h in range(6, 22)]  # Від 06:00 до 21:00
    buttons = [
        [InlineKeyboardButton(text=t, callback_data=f"{prefix}_{t}")] for t in times
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)