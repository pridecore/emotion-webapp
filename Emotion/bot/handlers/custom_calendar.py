from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_calendar.simple_calendar import SimpleCalendar, SimpleCalendarCallback
from datetime import date
import calendar
from aiogram import Router

router = Router()

DAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]

class CustomCalendar(SimpleCalendar):
    def __init__(self, working_days=None, busy_days=None, **kwargs):
        self.working_days = working_days or []
        self.busy_days = busy_days or []
        self.firstweekday = calendar.MONDAY  # Тиждень починається з понеділка

        super().__init__(**kwargs)

    async def _build_days(self, year: int, month: int):
        month_calendar = calendar.Calendar(self.firstweekday).monthdayscalendar(year, month)

        keyboard = []

        # --- Панель з днями тижня ---
        keyboard.append([
            InlineKeyboardButton(text=day, callback_data="ignore") for day in DAY_NAMES
        ])

        # --- Дні місяця ---
        for week in month_calendar:
            row = []
            for day in week:
                if day == 0:
                    row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
                    continue

                # Іконки для статусу дня
                if day in self.busy_days:
                    label = f"× {day}"
                elif day in self.working_days:
                    label = f"✓ {day}"
                else:
                    label = f"🔒 {day}"

                row.append(
                    InlineKeyboardButton(
                        text=label,
                        callback_data=SimpleCalendarCallback(
                            act="DAY", year=year, month=month, day=day
                        ).pack()
                    )
                )
            keyboard.append(row)
        return keyboard

    async def start_calendar(self, year: int = None, month: int = None):
        year = year or date.today().year
        month = month or date.today().month

        # --- Стрілки перемикання місяців (без року!) ---
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1

        month_name = calendar.month_name[month]

        header = [
            InlineKeyboardButton(
                text="◀",
                callback_data=SimpleCalendarCallback(act="PREV-MONTH", year=prev_year, month=prev_month, day=1).pack()
            ),
            InlineKeyboardButton(text=f"{month_name}", callback_data="ignore"),
            InlineKeyboardButton(
                text="▶",
                callback_data=SimpleCalendarCallback(act="NEXT-MONTH", year=next_year, month=next_month, day=1).pack()
            )
        ]

        days = await self._build_days(year, month)

        keyboard = [header] + days

        return InlineKeyboardMarkup(inline_keyboard=keyboard)