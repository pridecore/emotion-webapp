from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.psychologist_states import PsychologistLogin
from bot.keyboards.psychologist_menu import get_psychologist_menu
from bot.keyboards.main_menu import get_main_menu
import json
import os
from bot.utils.pending_utils import load_pending_confirmations
pending_confirmations = load_pending_confirmations()


router = Router()

authorized_psychologists = set()

APPROVED_FILE = os.path.join("data", "approved_psychologists.json")

@router.message(F.text.lower() == "/login")
async def login_start(message: Message, state: FSMContext):
    await message.answer("👤 Введіть ваш логін:")
    await state.set_state(PsychologistLogin.waiting_for_login)

@router.message(PsychologistLogin.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("🔐 Введіть пароль:")
    await state.set_state(PsychologistLogin.waiting_for_password)

@router.message(PsychologistLogin.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    data = await state.get_data()
    login = data["login"]
    password = message.text

    # Зчитати з approved_psychologists.json
    with open("data/approved_psychologists.json", "r", encoding="utf-8") as f:
        approved = json.load(f)

    for p in approved:
        if p["login"] == login and p["password"] == password:
            authorized_psychologists.add(message.from_user.id)

            # --- Зберігаємо user_id якщо ще немає ---
            if "user_id" not in p or str(p["user_id"]) != str(message.from_user.id):
                p["user_id"] = message.from_user.id
                with open("data/approved_psychologists.json", "w", encoding="utf-8") as f:
                    json.dump(approved, f, indent=2, ensure_ascii=False)

            await state.clear()
            await message.answer("✅ Авторизація успішна! Ваш Telegram ID збережено.", reply_markup=get_psychologist_menu())
            return

    await message.answer("❌ Невірний логін або пароль. Спробуйте ще раз або натисніть /login")


@router.message(F.text == "📥 Нові запити")
async def show_new_requests(message: Message):
    approved_file = os.path.join("data", "approved_psychologists.json")
    requests_file = os.path.join("data", "requests.json")

    # Перевірка, чи є файл з психологами
    if not os.path.exists(approved_file):
        await message.answer("❌ Дані психологів не знайдено.")
        return

    # Отримання логіну психолога за user_id
    with open(approved_file, "r", encoding="utf-8") as f:
        approved = json.load(f)

    psychologist = next(
        (psy for psy in approved if str(psy.get("user_id")) == str(message.from_user.id)),
        None
    )

    if not psychologist:
        await message.answer("🔐 Спершу авторизуйтесь через /login")
        return

    psychologist_login = psychologist.get("login")

    # Читання запитів
    if not os.path.exists(requests_file):
        await message.answer("Немає нових запитів.")
        return

    with open(requests_file, "r", encoding="utf-8") as f:
        all_requests = json.load(f)

    # Фільтрація по психологу і статусу
    requests = [
        r for r in all_requests
        if r.get("psychologist_login") == psychologist_login and r.get("status") == "новий"
    ]

    if not requests:
        await message.answer("Немає нових запитів.")
        return

    # Виведення запитів
    for i, r in enumerate(requests, 1):
        text = (
            f"📄 <b>Запит {i}</b>\n"
            f"📅 <b>Створено:</b> {r['created_at']}\n"
            f"🔍 <b>Проблема:</b> {r['problem']}\n"
            f"⏳ <b>Тривалість:</b> {r['duration']}\n"
            f"🎯 <b>Очікування:</b> {r['expectations']}\n"
            f"🕒 <b>Дата і час:</b> {r['preferred_time']}"
        )
        await message.answer(text, parse_mode="HTML")

@router.message(F.text == "🗓 Мій графік")
async def manage_schedule(message: Message, state: FSMContext):
    fullname = None  # 👈 зміна
    file_path = os.path.join("data", "approved_psychologists.json")

    working_days_text = "немає даних"
    working_times_text = "немає даних"

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            all_data = json.load(f)

            for psy in all_data:
                if str(psy.get("user_id")) == str(message.from_user.id):
                    fullname = psy.get("fullname")  # 👈 додаємо
                    days_map = {
                        0: "Понеділок",
                        1: "Вівторок",
                        2: "Середа",
                        3: "Четвер",
                        4: "П’ятниця",
                        5: "Субота",
                        6: "Неділя"
                    }
                    working_days = psy.get("working_days", [])
                    working_times = psy.get("working_times", [])

                    if working_days:
                        working_days_text = ", ".join([days_map[d] for d in working_days])
                    if working_times:
                        working_times_text = ", ".join(working_times)
                    break

    if not fullname:
        await message.answer("❌ Ваш профіль психолога не знайдено.")
        return

    await message.answer(
        f"🗓 <b>Ваш поточний графік ({fullname}):</b>\n"
        f"<b>Робочі дні:</b> {working_days_text}\n"
        f"<b>Час:</b> {working_times_text}\n\n"
        "Якщо хочете змінити графік, зверніться до адміністратора",
        parse_mode="HTML"
    )

@router.message(F.text.startswith("👤"))
async def show_psychologist_profile(message: Message):
    file_path = os.path.join("data", "approved_psychologists.json")

    if not os.path.exists(file_path):
        await message.answer("❌ Дані психологів не знайдено.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        all_psy = json.load(f)

    # 🔍 Визначаємо, чий профіль показати
    text = message.text.strip()
    target_psy = None

    if text == "👤 Мій профіль":
        # Пошук за поточним user_id
        target_psy = next((p for p in all_psy if str(p.get("user_id")) == str(message.from_user.id)), None)
    elif "Профіль:" in text:
        query = text.replace("👤 Профіль:", "").strip()
        # Можна шукати за логіном або user_id
        target_psy = next(
            (p for p in all_psy if str(p.get("login", "")).lower() == query.lower() or str(p.get("user_id")) == query),
            None
        )

    if not target_psy:
        await message.answer("❌ Профіль не знайдено.")
        return

    # Дані
    login = target_psy.get("login", "—")
    fullname = target_psy.get("fullname", "—")
    education = target_psy.get("education", "—")
    additional = target_psy.get("experience_desc", "—")
    experience = target_psy.get("years", "—")
    price = target_psy.get("price", "—")
    languages = target_psy.get("languages", "—")
    languages_text = ", ".join(languages) if isinstance(languages, list) else str(languages)
    specs = target_psy.get("specializations", "—")
    specs_text = ", ".join(specs) if isinstance(specs, list) else str(specs)

    profile_text = (
        f"👤 <b>Профіль психолога</b>\n\n"
        f"🆔 <b>Логін:</b> {login}\n"
        f"👩‍⚕️ <b>ПІБ:</b> {fullname}\n"
        f"📚 <b>Освіта:</b> {education}\n"
        f"💼 <b>Досвід:</b> {experience} років\n"
        f"💰 <b>Ціна:</b> {price} грн\n"
        f"🌍 <b>Мови консультацій:</b> {languages_text}\n"
        f"🎯 <b>Напрями роботи:</b> {specs_text}\n\n"
        f"📝 <b>Професійна інформація:</b>\n{additional}"
    )

    photo_url = target_psy.get("photo")
    if photo_url and photo_url.startswith("http"):
        try:
            await message.answer_photo(photo_url, caption=profile_text, parse_mode="HTML")
        except Exception as e:
            await message.answer(f"{profile_text}\n\n⚠️ Не вдалося надіслати фото: {e}", parse_mode="HTML")
    else:
        await message.answer(profile_text, parse_mode="HTML")

@router.message(F.text == "🚪 Вийти")
async def logout_button(message: Message):
    if message.from_user.id in authorized_psychologists:
        authorized_psychologists.remove(message.from_user.id)
        await message.answer("🔓 Ви вийшли з кабінету психолога.")
    else:
        await message.answer("⚠️ Ви не були авторизовані.")

    # Зміна клавіатури на клієнтське меню
    await message.answer(
        "👋 Ви повернулись у головне меню. Оберіть дію:",
        reply_markup=get_main_menu()
    )