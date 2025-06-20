from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
import calendar
import json
import os

from bot.states.client_states import ClientForm
from bot.handlers.finalize import finalize_consultation_request

router = Router()

SLOTS_FILE = os.path.join("data", "calendar_slots.json")
APPROVED_FILE = os.path.join("data", "approved_psychologists.json")

if not os.path.exists(SLOTS_FILE):
    with open(SLOTS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def load_slots():
    with open(SLOTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_slots(slots):
    with open(SLOTS_FILE, "w", encoding="utf-8") as f:
        json.dump(slots, f, indent=2, ensure_ascii=False)

def get_psychologist_data(login):
    with open(APPROVED_FILE, "r", encoding="utf-8") as f:
        approved = json.load(f)
    return next((p for p in approved if p["login"] == login), None)

def generate_month_keyboard(year: int, month: int, slots: dict, working_days: list = [], working_times: list = [], prefix: str = "day"):
    _, num_days = calendar.monthrange(year, month)
    days = []

    # --- Панель днів тижня ---
    week_header = [InlineKeyboardButton(text=day, callback_data="ignore") for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]]
    days.append(week_header)

    week = []

    for day in range(1, num_days + 1):
        date_obj = datetime(year, month, day)
        date_str = date_obj.strftime('%Y-%m-%d')

        # Часи, які ще доступні (порівняння з графіком психолога)
        booked_times = slots.get(date_str, [])
        available_times = [t for t in working_times if t not in booked_times]

        if available_times:
            label = f"🟢{day:02}"  # Є хоча б один вільний час
        else:
            label = f"🔴{day:02}"  # Усі години зайняті


        week.append(InlineKeyboardButton(
            text=label,
            callback_data=f"{prefix}_{date_str}"
        ))

        if date_obj.weekday() == 6 or day == num_days:
            # Додаємо тиждень
            days.append(week)
            week = []

    # --- Перемикач місяців ---
    prev_month = month - 1
    next_month = month + 1

    # Якщо менше січня, залишаємся в січні
    if prev_month < 1:
        prev_month = 1

    # Якщо більше грудня, залишаємось в грудні
    if next_month > 12:
        next_month = 12

    # Кнопки перемикання лише по місяцях в межах року
    switch_row = [
        InlineKeyboardButton(text="«", callback_data=f"{prefix}_calendar_{year}_{prev_month}"),
        InlineKeyboardButton(text=f"{calendar.month_name[month]} {year}", callback_data="ignore"),
        InlineKeyboardButton(text="»", callback_data=f"{prefix}_calendar_{year}_{next_month}")
    ]

    days.append(switch_row)
    return InlineKeyboardMarkup(inline_keyboard=days)

@router.message(F.text == "🗓 Мій календар")
@router.message(Command("calendar"))
async def show_calendar(message: Message, state: FSMContext):
    data = await state.get_data()
    psychologist_login = data.get("psychologist_login")

    if not psychologist_login:
        await message.answer("⚠ Спершу оберіть психолога.")
        return

    psychologist = get_psychologist_data(psychologist_login)
    if not psychologist:
        await message.answer("⚠ Не вдалося знайти психолога.")
        return

    today = datetime.today()
    slots = load_slots()

    keyboard = generate_month_keyboard(
        today.year,
        today.month,
        slots,
        working_days=psychologist.get("working_days", []),
        working_times=psychologist.get("working_times", []),
        prefix="form"
    )

    await message.answer("📅 Оберіть день консультації:", reply_markup=keyboard)
    await state.set_state(ClientForm.writing_preferred_time)

@router.callback_query(F.data.startswith("form_calendar_"))
async def form_change_month(callback: CallbackQuery, state: FSMContext):
    _, _, year, month = callback.data.split("_")
    data = await state.get_data()
    psychologist_login = data.get("psychologist_login")
    psychologist = get_psychologist_data(psychologist_login)

    slots = load_slots()
    keyboard = generate_month_keyboard(
        int(year),
        int(month),
        slots,
        working_days=psychologist.get("working_days", []),
        prefix="form"
    )

    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("form_") & ~F.data.startswith("form_calendar_"))
async def form_pick_date(callback: CallbackQuery, state: FSMContext):
    date = callback.data.replace("form_", "")
    data = await state.get_data()
    psychologist_login = data.get("psychologist_login")
    psychologist = get_psychologist_data(psychologist_login)

    if not psychologist:
        await callback.message.answer("⚠ Не вдалося знайти психолога.")
        return

    working_times = psychologist.get("working_times", [])
    slots = load_slots()
    booked = slots.get(date, [])

    buttons = []
    for time in working_times:
        if time in booked:
            buttons.append([InlineKeyboardButton(text=f"❌ {time}", callback_data="ignore")])
        else:
            buttons.append([InlineKeyboardButton(text=f"🕒 {time}", callback_data=f"form_time_{date}_{time}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer(f"🗓 Оберіть час для <b>{date}</b>:", reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("form_time_"))
async def form_pick_time(callback: CallbackQuery, state: FSMContext):
    _, date, time = callback.data.split("_", 2)
    await state.update_data(preferred_time=f"{date} {time}")

    slots = load_slots()
    if date not in slots:
        slots[date] = []
    slots[date].append(time)
    save_slots(slots)

    await callback.message.answer(f"✅ Ви обрали: <b>{date}</b> о <b>{time}</b>", parse_mode="HTML")
    await callback.answer()

    await finalize_consultation_request(callback.message, state)

@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()