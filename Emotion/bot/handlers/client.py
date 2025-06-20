from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton
)


from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from datetime import datetime, date
import json
import os
import random
import asyncio

# Імпорти з проєкту
from bot.keyboards.main_menu import get_main_menu
from bot.keyboards.specialization import get_all_specializations_keyboard, get_spec_by_key

from bot.states.client_states import ClientForm, Booking, FeedbackForm, ReminderForm
from bot.handlers.custom_calendar import CustomCalendar, SimpleCalendarCallback
from bot.utils.pending_utils import load_pending_confirmations
from bot.utils.jitsi import generate_jitsi_link

from bot.services.wayforpay_service import create_invoice

from aiogram.types import ReplyKeyboardRemove
from bot.utils.payment_checker import check_payment_after_delay


from filelock import FileLock



ADMIN_ID=7761542233  # заміни на свій Telegram ID

affirmations = [
    "🌟 Я достатньо хороший, щоби жити щасливо просто зараз.",
    "💫 Мої думки створюють мою реальність, і я обираю думати позитивно.",
    "🌱 Я заслуговую на турботу, повагу й любов.",
    "🔥 Я зростаю, навчаюсь і стаю кращою версією себе.",
    "🧘 Моє тіло розслаблене, мій розум спокійний, моя душа світла.",
    "🌈 Я довіряю життю та відкритий до нових можливостей.",
    "✨ Я сильна, мудра і здатна впоратись із будь-чим.",
    "🤍 Я приймаю себе повністю — з усіма світлими й темними сторонами.",
    "🪞 Я не повинен бути ідеальним, щоб бути цінним.",
    "💖 Моя вразливість — це моя сила.",
    "🛡️ Я впораюсь з будь-яким викликом.",
    "🚀 Я маю все, щоб рухатися вперед.",
    "🦶 Кожен мій крок — це сміливість обирати себе.",
    "🏆 Я вірю в себе, навіть коли інші сумніваються.",
    "📈 Моя впевненість зростає щодня.",
    "👂 Я заслуговую на любов — від себе і від інших.",
    "🫂 Мені дозволено відпочивати й піклуватися про себе.",
    "💌 Я — свій найкращий друг.",
    "🧴 Турбота про себе — це не егоїзм, а необхідність.",
    "🎧 Я слухаю свої потреби з повагою і ніжністю.",
    "🌊 Я дозволяю собі відчувати все, що відчувається.",
    "🎭 Мої емоції мають значення.",
    "💎 Я зберігаю спокій навіть у складних ситуаціях.",
    "🌫️ Усі емоції — нормальні. Я даю їм місце.",
    "🫶 Навіть коли боляче — я не один.",
    "🚦 Я маю право робити вибір, який підходить саме мені.",
    "🧭 Кожне моє рішення — це прояв турботи про себе.",
    "🐢 Я рухаюся у своєму темпі — і цього достатньо.",
    "🔁 Я не застряг — я в процесі росту.",
    "⏳ Я заслуговую на другий шанс.",
    "🌅 Мій день починається з любові до себе.",
    "☀️ Сьогодні — хороший день, щоби жити.",
    "🤲 Я відпускаю контроль і обираю довіру.",
    "🪶 Те, що зі мною трапляється, не визначає мою цінність.",
    "🧬 Я — цінний і важливий просто тому, що я є.",
    "🤝 Я гідний поваги у стосунках.",
    "🗣️ Я заслуговую бути почутим.",
    "🧱 Мої межі — важливі і мають значення.",
    "🙅 Я маю право відмовити без почуття провини.",
    "🫂 Я створюю здорові зв’язки, що наповнюють мене.",
    "🧹 Я відпускаю те, що більше не служить мені.",
    "📉 Я не є своїми помилками.",
    "🔄 Я можу почати знову — у будь-який момент.",
    "📚 Я вдячний за досвід, який зробив мене сильнішим.",
    "🪷 Я обираю зцілення замість повторення.",
    "🗺️ Моє майбутнє сповнене можливостей.",
    "🚪 Я відкритий до нового і гармонійного.",
    "🌪️ Я не боюсь змін — я росту разом з ними.",
    "🎡 Моє життя має сенс.",
    "🕊️ Я довіряю, що все складається на краще для мене.",
    "💠 У мені більше сили, ніж я думаю.",
    "🌻 Я вже не той, ким був — я зростаю.",
    "🫧 У моєму серці є спокій.",
    "📦 Я створюю простір для себе і в собі.",
    "🔮 Мій шлях — унікальний, і я поважаю його."
]

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    if message.chat.type != "private":
        return

    photo_path = os.path.join("img", "logo.png")

    caption = (
        "<b>👋 Привіт! Я Emotion — бот психологічної підтримки.</b>\n\n"
        "Тут ти можеш:\n"
        "🧠 Записатися на консультацію до психолога\n"
        "💬 Обрати спеціаліста під свою ситуацію (тривожність, стосунки, депресія, самооцінка тощо)\n"
        "📅 Переглянути свої бронювання та консультації\n"
        "✨ Отримати афірмацію дня для натхнення\n"
        "🔎 Переглядати календар своїх консультацій\n\n"
        "У нас працюють професійні психологи з багаторічним досвідом, різними напрямками роботи й гнучким графіком.\n\n"
        "🔒 Твої дані конфіденційні. Ми завжди на зв’язку, щоб допомогти тобі знайти рішення 💚\n\n"
        "Готовий розпочати? Натискай меню нижче 👇"
    )

    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer(
            caption,
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )

@router.message(F.text == "/help")
async def handle_help(message: Message, state: FSMContext):
    await message.answer(
        "❓ Якщо маєш запитання, пропозицію чи скаргу — просто напиши повідомлення у відповідь на це.\n\n"
        "📌 Наприклад:\n"
        "• «Я не отримав відповідь від психолога»\n"
        "• «Чи можу я змінити дату консультації?»\n"
        "• «Пропозиція щодо покращення функцій бота»\n\n"
        "Ми читаємо кожне звернення і відповімо максимально швидко 💚"
    )
    await state.set_state(FeedbackForm.waiting_feedback)


@router.message(F.text == "🧠 Записатись на консультацію")
async def choose_all_specializations(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🧠 Оберіть запити, які вас турбують:", reply_markup=get_all_specializations_keyboard())

@router.message(F.text == "✨ Афірмація дня")
async def affirmation_of_day(message: Message):

    affirmation = random.choice(affirmations)

    # Надсилаємо афірмацію
    await message.answer(affirmation)

    # Пропозиція підписки
    await message.answer(
        "🕒 Хочеш отримувати афірмацію щодня у зручний час?\n"
        "Натисни кнопку нижче, щоб обрати час:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔔 Налаштувати розклад", callback_data="setup_affirmation_reminder")]
            ]
        )
    )
@router.callback_query(F.data == "setup_affirmation_reminder")
async def start_reminder_via_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🕒 Введіть час, коли ви хочете отримувати афірмацію щодня (наприклад 08:00):"
    )
    await state.set_state(ReminderForm.waiting_for_time)
    await callback.answer()

@router.message(F.text == "🕒 Афірмація за розкладом")
async def start_reminder_setup(message: Message, state: FSMContext):
    await message.answer(
        "🕒 Введіть час, коли ви хочете отримувати афірмацію щодня (у форматі <b>HH:MM</b>, наприклад <b>08:00</b>):",
        parse_mode="HTML"
    )
    await state.set_state(ReminderForm.waiting_for_time)

@router.message(ReminderForm.waiting_for_time)
async def save_affirmation_time(message: Message, state: FSMContext):
    user_time = message.text.strip()

    try:
        # Перевірка правильного формату HH:MM
        datetime.strptime(user_time, "%H:%M")

        schedule_file = "data/affirmation_schedule.json"
        os.makedirs("data", exist_ok=True)

        # Завантажити або створити словник розкладу
        if os.path.exists(schedule_file):
            with open(schedule_file, "r", encoding="utf-8") as f:
                try:
                    schedule = json.load(f)
                    if not isinstance(schedule, dict):
                        schedule = {}  # Якщо файл випадково містив список або інший тип
                except json.JSONDecodeError:
                    schedule = {}
        else:
            schedule = {}

        # Записати час під user_id
        schedule[str(message.from_user.id)] = user_time

        with open(schedule_file, "w", encoding="utf-8") as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)

        await message.answer(f"✅ Готово! Тепер щодня о {user_time} ви будете отримувати афірмацію 🌿")
        await state.clear()

    except ValueError:
        await message.answer("⚠️ Невірний формат. Спробуйте ще раз (наприклад 08:00):")


@router.message(F.text == "/manage_affirmation")
async def manage_affirmation_cmd(message: Message):
    await manage_affirmation_reminder(message)

@router.message(F.text == "⚙️ Керування афірмаціями")
async def manage_affirmation_reminder(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Змінити час", callback_data="change_affirmation_time")],
        [InlineKeyboardButton(text="❌ Вимкнути надсилання", callback_data="cancel_affirmation_schedule")]
    ])
    await message.answer("⚙️ Що ви хочете зробити?", reply_markup=keyboard)

@router.callback_query(F.data == "change_affirmation_time")
async def change_affirmation_time(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🕒 Введіть новий час у форматі <b>HH:MM</b> (наприклад 08:00):", parse_mode="HTML")
    await state.set_state(ReminderForm.waiting_for_time)
    await callback.answer()

@router.callback_query(F.data == "cancel_affirmation_schedule")
async def cancel_affirmation_schedule(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    schedule_file = "data/affirmation_schedule.json"

    if os.path.exists(schedule_file):
        with open(schedule_file, "r", encoding="utf-8") as f:
            try:
                schedule = json.load(f)
                if user_id in schedule:
                    del schedule[user_id]
                    with open(schedule_file, "w", encoding="utf-8") as fw:
                        json.dump(schedule, fw, ensure_ascii=False, indent=2)
                    await callback.message.answer("❌ Ви успішно вимкнули щоденне надсилання афірмацій.")
                else:
                    await callback.message.answer("ℹ️ У вас не налаштовано афірмації.")
            except json.JSONDecodeError:
                await callback.message.answer("⚠️ Помилка читання розкладу.")
    else:
        await callback.message.answer("ℹ️ У вас не налаштовано афірмації.")

    await callback.answer()


@router.message(F.text == "/bookings")
async def bookings_command_alias(message: Message):
    await my_sessions(message)

@router.message(F.text == "📖 Мої бронювання")
async def my_sessions(message: Message):
    def format_datetime(date_str):
        try:
            dt = datetime.strptime(date_str, "%d.%m.%Y %H:%M")
            return dt.strftime("%d.%m.%Y %H:%M")
        except:
            return date_str  # якщо формат не підійшов

    file_path = os.path.join("data", "requests.json")
    image_path = os.path.join("img", "session.jpg")  # 🖼 Замінити на реальне зображення

    if not os.path.exists(file_path):
        await message.answer("У вас поки немає жодної консультації 😊")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    user_data = [item for item in all_data if item["client_id"] == message.from_user.id]

    if not user_data:
        await message.answer("У вас поки немає жодної консультації 😊")
        return

    for i, item in enumerate(user_data, 1):
        created = format_datetime(item.get("created_at", "—"))
        preferred = format_datetime(item.get("preferred_time", "—"))

        text = (
            f"📄 <b>Сесія {i}</b>\n"
            f"📅 <b>Створено:</b> {created}\n"
            f"🔍 <b>Проблема:</b> {item['problem']}\n"
            f"⏳ <b>Тривалість:</b> {item['duration']}\n"
            f"🎯 <b>Очікування:</b> {item['expectations']}\n"
            f"🕒 <b>Час консультації:</b> {preferred}\n"
            f"📌 <b>Статус:</b> {item['status'].capitalize()}"
        )

        if os.path.exists(image_path):
            photo = FSInputFile(image_path)
            await message.answer_photo(photo=photo, caption=text, parse_mode="HTML")
        else:
            await message.answer(text, parse_mode="HTML")


@router.message(F.text == "/profile")
async def profile_command_alias(message: Message):
    await my_profile(message)

@router.message(F.text == "👤 Мій профіль")
async def my_profile(message: Message):
    user = message.from_user
    username = user.username or "—"
    full_name = user.full_name
    user_id = user.id
    file_path = os.path.join("data", "requests.json")

    user_requests = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            all_requests = json.load(f)
            user_requests = [x for x in all_requests if x.get("client_id") == user_id]

    count = len(user_requests)

    first_date = "—"
    last_date = "—"
    most_common_problem = "—"

    if user_requests:
        sorted_requests = sorted(user_requests, key=lambda x: x.get("created_at", ""))
        first_date = sorted_requests[0].get("created_at", "—")
        last_date = sorted_requests[-1].get("created_at", "—")

        # Найчастіша проблема
        from collections import Counter
        problems = [x.get("problem", "").strip() for x in user_requests if x.get("problem")]
        if problems:
            most_common_problem = Counter(problems).most_common(1)[0][0]

    profile_text = (
        f"👤 <b>Ваш профіль</b>\n"
        f"🧾 <b>Ім’я:</b> {full_name}\n"
        f"🔗 <b>Username:</b> @{username}\n\n"
        f"📄 <b>Кількість заявок:</b> {count}\n"
        f"📅 <b>Перша заявка:</b> {first_date}\n"
        f"🕓 <b>Остання заявка:</b> {last_date}\n"
        f"🔍 <b>Найчастіша тема:</b> {most_common_problem}"
    )

    # Шлях до фото клієнта
    photo_path = os.path.join("img", "clients", f"{user_id}.jpg")

    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=profile_text, parse_mode="HTML")
    else:
        await message.answer(profile_text, parse_mode="HTML")

@router.message(F.text == "/about")
async def about_command_alias(message: Message):
    # Просто викликаємо існуючий хендлер
    await about_bot(message)

@router.message(F.text == "ℹ️ Про бота")
async def about_bot(message: Message):
    photo_path = os.path.join("img", "about_cover.jpg")  # 🔄 Замініть на фактичну назву файлу

    caption = (
        "<b>ℹ️ Про бот Emotion</b>\n\n"
        "Emotion — це не просто бот. Це місце, де тебе почують.\n\n"
        "Ми створили його для таких моментів, коли хочеться зупинитися, видихнути і просто бути чесним(ою) із собою.\n\n"
        "Буває, що все навалюється — тривога, самотність, втома, розгубленість у стосунках або просто відчуття, що щось не так. У такі моменти важливо знати: ти не один(одна).\n\n"
        "Тут ти можеш:\n"
        "• 🧠 знайти психолога, з яким буде легко говорити\n"
        "• ✨ отримати слова підтримки, коли важко\n"
        "• 📖 переглянути свої консультації або просто побути в тиші\n\n"
        "Ми не будемо повчати чи нав'язувати. Просто поруч — з досвідом, турботою і бажанням підтримати.\n\n"
        "Твої повідомлення не зникають в нікуди. Ми читаємо кожне. І щиро радіємо, коли ти робиш крок до себе.\n\n"
        "🌿 Дякуємо, що ти тут. Якщо буде важко — пиши. Якщо добре — теж пиши 🙂\n\n"
        "Твоя команда Emotion 💚"
    )

    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=caption, parse_mode="HTML")
    else:
        await message.answer(caption, parse_mode="HTML")


@router.message(F.text == "📤 Поділитися ботом")
async def share_bot(message: Message):
    bot_username = (await message.bot.get_me()).username
    share_text = "Привіт! Я користуюсь ботом Emotion для психологічної підтримки. Спробуй і ти 💚"
    bot_link = f"https://t.me/{bot_username}?start=share"

    # Фото перед описом
    photo_path = os.path.join("img", "share_cover.jpg")  # заміни на актуальне ім’я файлу

    caption = (
        "🔗 Поділись ботом з близькими:\n"
        "Раптом комусь поруч саме зараз потрібна підтримка 💚\n\n"
        f"👉 {bot_link}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📨 Надіслати другу", switch_inline_query=share_text)]
    ])

    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=caption, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer(caption, reply_markup=keyboard)

@router.message(F.text == "/contact")
async def contact_command_alias(message: Message, state: FSMContext):
    await feedback_start(message, state)

@router.message(F.text == "✉️ Зворотний зв’язок")
async def feedback_start(message: Message, state: FSMContext):
    # Шлях до зображення
    photo_path = os.path.join("img", "feedback_cover.jpg")  # заміни на актуальний файл

    caption = (
        "✏️ Напишіть повідомлення або відгук, який ви хочете передати нашій команді.\n\n"
        "📌 Ви можете написати:\n"
        "• Пропозицію щодо покращення\n"
        "• Повідомити про помилку\n"
        "• Поділитися враженнями або побажанням 💬"
    )

    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=caption, parse_mode="HTML")
    else:
        await message.answer(caption)

    await state.set_state(FeedbackForm.waiting_feedback)

# Обробка відповіді користувача
@router.message(FeedbackForm.waiting_feedback)
async def feedback_receive(message: Message, state: FSMContext):
    user = message.from_user
    feedback_text = message.text

    username_display = f"@{user.username}" if user.username else "—"

    try:
        await message.bot.send_message(
            ADMIN_ID,
            f"📨 <b>Нове повідомлення від користувача</b>\n"
            f"👤 <b>Імʼя:</b> {user.full_name}\n"
            f"🔗 <b>Username:</b> {username_display}\n\n"
            f"<i>«{feedback_text}»</i>",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer("⚠️ Не вдалося надіслати повідомлення адміну.")
        print(f"[❌ ERROR] ADMIN_ID = {ADMIN_ID}; {e}")
    else:
        await message.answer("💌 Ваше повідомлення вже в надійних руках. Дякуємо, що поділилися 🌿")

    await state.clear()


@router.callback_query(F.data.startswith("toggle_all:"))
async def toggle_all_specializations(callback: CallbackQuery, state: FSMContext):
    spec = callback.data.replace("toggle_all:", "")
    data = await state.get_data()
    selected = data.get("selected_all", [])

    if spec in selected:
        selected.remove(spec)
    else:
        selected.append(spec)

    await state.update_data(selected_all=selected)
    await callback.message.edit_text("🧠 Оберіть запити, які вас турбують:", reply_markup=get_all_specializations_keyboard(selected))
    await callback.answer()

@router.callback_query(F.data == "show_all")
async def show_all_selected(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_specs = data.get("selected_all", [])

    if not selected_specs:
        await callback.answer("⚠️ Ви не обрали жодного напряму", show_alert=True)
        return

    with open("data/approved_psychologists.json", "r", encoding="utf-8") as f:
        all_psychologists = json.load(f)

    matched_logins = []
    for psy in all_psychologists:
        specs = [s.strip().lower() for s in psy.get("specializations", "").split(",")]
        if any(spec.lower() in specs for spec in selected_specs):
            matched_logins.append(psy["login"])

    if not matched_logins:
        await callback.answer("😔 Немає фахівців за цими напрямами", show_alert=True)
        return

    base_url = "https://pridecore.github.io/emotion-webapp/Emotion/"
    full_url = f"{base_url}?logins={','.join(matched_logins)}"

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🧠 Обрати психолога", web_app=WebAppInfo(url=full_url))]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await callback.message.answer(
        "🔗 <b>Оберіть психолога з тих, хто працює з обраними темами:</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_categories")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("⬅️ Повернулись у головне меню", reply_markup=get_main_menu())
    await callback.answer()

@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data.startswith("t:"))
async def toggle_spec(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    spec = get_spec_by_key(key)

    data = await state.get_data()
    selected = data.get("selected_all", [])

    if spec in selected:
        selected.remove(spec)
    else:
        selected.append(spec)

    await state.update_data(selected_all=selected)
    await callback.message.edit_text("🧠 Оберіть запити, які вас турбують та:", reply_markup=get_all_specializations_keyboard(selected))
    await callback.answer()

@router.message(F.web_app_data)
async def handle_webapp_selection(message: Message):
    print("🟡 WebApp callback triggered")
    print("📨 message.text:", message.text)
    print("📦 message.web_app_data:", message.web_app_data)

    try:
        webapp_data = getattr(message.web_app_data, 'data', None)
        if not webapp_data:
            print("⚠️ Дані з WebApp не отримано або порожні.")
            await message.answer("⚠️ Дані з веб-додатку не отримано.")
            return

        print("📦 message.web_app_data.data:", webapp_data)
        data = json.loads(webapp_data)
        login = data.get("login")

        if not login:
            print("❗️ Поле 'login' відсутнє у JSON")
            await message.answer("⚠️ Не вказано логін психолога.")
            return

        print(f"🔍 Обраний логін психолога: {login}")
        json_path = os.path.join("data", "approved_psychologists.json")

        if not os.path.exists(json_path):
            await message.answer("❌ База даних фахівців не знайдена.")
            return

        with open(json_path, "r", encoding="utf-8") as f:
            psychologists = json.load(f)

        psy = next((p for p in psychologists if p["login"] == login), None)

        if not psy:
            await message.answer("❌ Психолога не знайдено.")
            return

        print("✅ Психолог знайдений:", psy["fullname"])

        # Опис психолога
        text = (
            f"<b>{psy['fullname']}</b>\n\n\n"
            f"💬 <i>{psy.get('experience_desc', '—')}</i>\n\n"
            f"📚 <b>Освіта:</b> {psy.get('education', '—')}\n\n"
            f"🎓 <b>Стаж:</b> {psy.get('years', '—')} років\n\n"
            f"🧠 <b>Напрями роботи:</b> {psy.get('directions_detailed', '—')}\n\n"
            f"🌍 <b>Мови:</b> {psy.get('languages', '—')}\n\n"
            f"💵 <b>Вартість однієї консультації (50хв):</b> {psy.get('price', '—')} грн"
        )

        photo_value = psy.get("photo", "")
        print("🖼 Фото:", photo_value)

        if photo_value.startswith("http"):
            print("🌐 Фото є посиланням — надсилаємо через URL")
            await message.answer_photo(photo=photo_value, caption=text, parse_mode="HTML")

        else:
            photo_path = os.path.join("img", photo_value)
            if os.path.exists(photo_path):
                photo = FSInputFile(photo_path)
                await message.answer_photo(photo=photo, caption=text, parse_mode="HTML")
            else:
                print("⚠️ Фото не знайдено — надсилаємо лише текст")
                await message.answer(text, parse_mode="HTML")

        # Кнопка для переходу до анкети
        choose_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="📝 Перейти до анкети",
                    callback_data=f"choose_{login}"
                )]
            ]
        )

        await message.answer(
            "✅ Ви обрали психолога.\n Деталі вище ⬆️\n\nГотові заповнити анкету для першої консультації?",
            reply_markup=choose_keyboard
        )

    except json.JSONDecodeError:
        print("❌ JSONDecodeError — неправильний формат WebApp data")
        await message.answer("❌ Дані з WebApp мають некоректний формат.")
    except Exception as e:
        print(f"🚨 Несподівана помилка у WebApp selection: {e}")
        await message.answer("🚫 Сталася помилка.")


# --- Початок анкети ---
@router.callback_query(F.data.startswith("choose_"))
async def start_form(callback: CallbackQuery, state: FSMContext):
    psychologist_login = callback.data.replace("choose_", "")
    await state.update_data(psychologist_login=psychologist_login)
    await callback.message.answer("1️⃣ Опишіть одним реченням Ваш стан:")
    await state.set_state(ClientForm.writing_expectations)
    await callback.answer()

@router.message(ClientForm.writing_expectations)
async def form_expectations(message: Message, state: FSMContext):
    await state.update_data(expectations=message.text)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="a) Щотижня")],
            [KeyboardButton(text="b) Раз на два тижні")],
            [KeyboardButton(text="c) Раз на місяць")],
            [KeyboardButton(text="d) Ще не вирішив(ла)")]
        ],
        resize_keyboard=True
    )
    await message.answer("2️⃣ Як часто ви готові відвідувати сесії?", reply_markup=kb)
    await state.set_state(ClientForm.frequency)

@router.message(ClientForm.frequency)
async def form_frequency(message: Message, state: FSMContext):
    await state.update_data(frequency=message.text)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="a) Підтримуючий і м’який")],
            [KeyboardButton(text="b) Прямий і структурований")],
            [KeyboardButton(text="c) Гнучкий, залежно від ситуації")]
        ],
        resize_keyboard=True
    )
    await message.answer("3️⃣ Який стиль спілкування психолога вам комфортніший?", reply_markup=kb)
    await state.set_state(ClientForm.communication_style)


@router.message(ClientForm.communication_style)
async def form_style(message: Message, state: FSMContext):
    await state.update_data(communication_style=message.text)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="a) 14-18"), KeyboardButton(text="b) 19-29")],
            [KeyboardButton(text="c) 30-59"), KeyboardButton(text="d) 60+")]
        ],
        resize_keyboard=True
    )
    await message.answer("4️⃣ Ваш вік?", reply_markup=kb)
    await state.set_state(ClientForm.final_confirmation)



@router.message(ClientForm.final_confirmation)
async def form_save_data(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    data = await state.get_data()

    user_data = {
        "user_id": message.from_user.id,
        "name": message.from_user.full_name,
        "username": message.from_user.username,
        "problem": data.get("problem"),
        "duration": data.get("duration"),
        "expectations": data.get("expectations"),
        "frequency": data.get("frequency"),
        "communication_style": data.get("communication_style"),
        "age": data.get("age")
    }

    file_path = "data/client_questionnaires.json"
    os.makedirs("data", exist_ok=True)

    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
                if not isinstance(existing, list):
                    existing = [existing]
        else:
            existing = []
    except (json.JSONDecodeError, FileNotFoundError):
        existing = []

    existing.append(user_data)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    # ✅ Повідомлення з видаленням клавіатури
    await message.answer(
        "✅ Анкету збережено.\n\n"
        "🗓 Зараз оберіть зручну дату та час для консультації.\n"
        "⏳ Увага: запис можливий щонайменше за <b>30 хвилин до початку</b> консультації.",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

    # Перехід до вибору дати
    await form_expectations(message, state)

# --- ОНОВЛЕНА логіка busy_days у form_expectations ---
@router.message(ClientForm.writing_expectations)
async def form_expectations(message: Message, state: FSMContext):
    await state.update_data(expectations=message.text)

    today = date.today()
    current_year, current_month = today.year, today.month

    data = await state.get_data()
    psychologist_login = data.get("psychologist_login")

    with open("data/approved_psychologists.json", "r", encoding="utf-8") as f:
        psychologists = json.load(f)

    psych = next((p for p in psychologists if p["login"] == psychologist_login), None)
    if not psych:
        await message.answer("⚠ Психолога не знайдено.")
        return

    working_days = psych.get("working_days", [])
    working_times = psych.get("working_times", [])

    busy_slots = {}
    if os.path.exists("data/requests.json"):
        with open("data/requests.json", "r", encoding="utf-8") as f:
            for req in json.load(f):
                if req["psychologist_login"] == psychologist_login:
                    dt = datetime.strptime(req["preferred_time"], "%d.%m.%Y %H:%M")
                    day = dt.day
                    busy_slots.setdefault(day, []).append(dt.strftime("%H:%M"))

    available_days = {}
    for day in range(1, 32):
        try:
            d = date(current_year, current_month, day)
            if d.weekday() in working_days:
                busy = busy_slots.get(day, [])
                free_count = len(working_times) - len(busy)
                if free_count > 0:
                    available_days[day] = free_count
        except:
            continue

    await state.update_data(
        working_times=working_times,
        available_days=available_days
    )

    await message.answer(
        "🗓 Оберіть зручну дату для консультації (ви можете обрати час не пізніше, ніж за <b>30 хвилин до початку</b>):",
        reply_markup=await CustomCalendar(
            working_days=list(available_days.keys()),
            busy_days=[]
        ).start_calendar(year=current_year, month=current_month),
        parse_mode="HTML"
    )
    await state.set_state(Booking.choosing_date)


@router.callback_query(SimpleCalendarCallback.filter(F.act.in_(["PREV-MONTH", "NEXT-MONTH"])), Booking.choosing_date)
async def change_month(callback_query: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    new_year = callback_data.year
    new_month = callback_data.month

    data = await state.get_data()
    psychologist_login = data.get("psychologist_login")

    # Завантаження психолога
    psychologist_file = os.path.join("data", "approved_psychologists.json")
    with open(psychologist_file, "r", encoding="utf-8") as f:
        psychologists = json.load(f)
    psych_data = next((p for p in psychologists if p["login"] == psychologist_login), None)

    working_weekdays = psych_data.get("working_days", [])
    working_times = psych_data.get("working_times", [])

    # Визначення робочих днів нового місяця
    working_days = []
    for day in range(1, 32):
        try:
            d = date(new_year, new_month, day)
            if d.weekday() in working_weekdays:
                working_days.append(day)
        except:
            continue

    # Визначення зайнятих дат у новому місяці
    busy_days = set()
    requests_file = os.path.join("data", "requests.json")
    if os.path.exists(requests_file):
        with open(requests_file, "r", encoding="utf-8") as f:
            all_requests = json.load(f)
            for item in all_requests:
                if item["psychologist_login"] == psychologist_login and "preferred_time" in item:
                    try:
                        dt = datetime.strptime(item["preferred_time"], "%d.%m.%Y %H:%M")
                        if dt.year == new_year and dt.month == new_month:
                            busy_days.add((dt.day, dt.strftime("%H:%M")))
                    except:
                        continue

    # Перетворення у формат CustomCalendar (тільки повністю зайняті дні)
    fully_busy_days = []
    for day in working_days:
        busy_hours = [time for d, time in busy_days if d == day]
        if len(busy_hours) >= len(working_times):
            fully_busy_days.append(day)

    await callback_query.message.edit_reply_markup(
        reply_markup=await CustomCalendar(
            working_days=working_days,
            busy_days=fully_busy_days
        ).start_calendar(year=new_year, month=new_month)
    )
    await callback_query.answer()

@router.callback_query(SimpleCalendarCallback.filter(F.act == "DAY"), Booking.choosing_date)
async def process_calendar(callback_query: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected_date_obj = date(callback_data.year, callback_data.month, callback_data.day)
    selected_date = selected_date_obj.strftime("%d.%m.%Y")

    data = await state.get_data()
    psychologist_login = data.get("psychologist_login")

    # Отримаємо дані про психолога
    with open("data/approved_psychologists.json", "r", encoding="utf-8") as f:
        psychologists = json.load(f)
    psych_data = next((p for p in psychologists if p["login"] == psychologist_login), None)

    if not psych_data:
        await callback_query.message.answer("⚠ Психолога не знайдено.")
        await callback_query.answer()
        return

    working_weekdays = psych_data.get("working_days", [])
    working_times = psych_data.get("working_times", [])

    # Перевіряємо, чи обраний день є робочим
    if selected_date_obj.weekday() not in working_weekdays:
        await callback_query.message.answer("❗ У цей день психолог не працює. Оберіть іншу дату.")
        await callback_query.answer()
        return

    # Завантажуємо всі бронювання на цю дату
    busy_times = []
    if os.path.exists("data/requests.json"):
        with open("data/requests.json", "r", encoding="utf-8") as f:
            all_requests = json.load(f)
            for item in all_requests:
                if (item["psychologist_login"] == psychologist_login and
                    item.get("preferred_time", "").startswith(selected_date)):
                    time_part = item["preferred_time"].split(" ")[1]
                    busy_times.append(time_part)

    # Обчислюємо доступні години
    free_times = [t for t in working_times if t not in busy_times]

    if not free_times:
        await callback_query.message.answer("❗ У цей день усі години зайняті. Оберіть інший день.")
        await callback_query.answer()
        return

    await state.update_data(preferred_date=selected_date, free_times=free_times)

    # Показуємо список доступних годин
    buttons = [
        [InlineKeyboardButton(text=time, callback_data=f"time_{time}")]
        for time in free_times
    ]

    await callback_query.message.answer(
        f"🕒 Оберіть вільний час для {selected_date}:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

    await state.set_state(Booking.choosing_time)
    await callback_query.answer()

# --- Завантажуємо поточні pending підтвердження ---
pending_confirmations = load_pending_confirmations()


@router.callback_query(F.data.startswith("time_"), Booking.choosing_time)
async def choose_time(callback_query: CallbackQuery, state: FSMContext):
    selected_time = callback_query.data.replace("time_", "")
    data = await state.get_data()

    preferred_date = data.get("preferred_date")
    psychologist_login = data.get("psychologist_login")
    preferred_datetime = f"{preferred_date} {selected_time}"

    # Перевірка зайнятості
    requests_file = os.path.join("data", "requests.json")
    busy = False
    if os.path.exists(requests_file):
        with open(requests_file, "r", encoding="utf-8") as f:
            all_requests = json.load(f)
            for item in all_requests:
                if item.get("psychologist_login") == psychologist_login and item.get("preferred_time") == preferred_datetime:
                    busy = True
                    break

    if busy:
        await callback_query.message.answer("❗ Цей час вже зайнятий. Оберіть інший.")
        await callback_query.answer()
        return

    await state.update_data(preferred_time=preferred_datetime)

    try:
        invoice_url, ref = create_invoice(
            user_id=callback_query.from_user.id,
            amount=1.0,
            product_name="Консультація психолога"
        )
    except Exception as e:
        print(f"❌ Помилка при створенні інвойсу: {e}")
        await callback_query.message.answer("⚠ Сталася помилка при створенні платіжного посилання. Спробуйте ще раз.")
        await callback_query.answer()
        return

    # Збереження платежу
    pending_file = os.path.join("data", "pending_payments.json")
    lock = FileLock(pending_file + ".lock")
    new_entry = {
        "user_id": callback_query.from_user.id,
        "orderReference": ref,
        "amount": 1.0,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }

    try:
        with lock:
            pending_data = []
            if os.path.exists(pending_file):
                with open(pending_file, "r", encoding="utf-8") as f:
                    pending_data = json.load(f)
            if not any(p["orderReference"] == ref for p in pending_data):
                pending_data.append(new_entry)
                with open(pending_file, "w", encoding="utf-8") as f:
                    json.dump(pending_data, f, indent=2, ensure_ascii=False)
            print(f"📝 Додано оплату: {ref}")
    except Exception as e:
        print(f"❌ Помилка збереження pending_payment: {e}")
        await callback_query.message.answer("⚠ Не вдалося зберегти інформацію про оплату.")
        await callback_query.answer()
        return

    await callback_query.message.answer(
        f"✅ Ви обрали: <b>{preferred_datetime}</b>\n"
        f"Сплатіть консультацію за посиланням:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="💳 Перейти до оплати", url=invoice_url)]]
        ),
        parse_mode="HTML"
    )

    await state.set_state(Booking.awaiting_payment)
    await state.update_data(invoice_url=invoice_url, order_reference=ref)

    asyncio.create_task(check_payment_after_delay(
        chat_id=callback_query.from_user.id,
        order_ref=ref,
        bot=callback_query.bot
    ))

    await callback_query.answer()

@router.callback_query(F.data == "pay_confirm", Booking.awaiting_payment)
async def confirm_payment(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = callback_query.from_user
    ref = data.get("order_reference")
    psychologist_login = data.get("psychologist_login")
    preferred_time = data.get("preferred_time")

    if not ref:
        await callback_query.message.answer("⚠ Помилка: платіжний код не знайдено.")
        await callback_query.answer()
        return

    payment_confirmed = False
    pending_file = os.path.join("data", "pending_payments.json")
    try:
        with FileLock(pending_file + ".lock"):
            if os.path.exists(pending_file):
                with open(pending_file, "r", encoding="utf-8") as f:
                    payments = json.load(f)
                    for item in payments:
                        if item.get("orderReference") == ref and item.get("user_id") == user.id and item.get("status") == "paid":
                            payment_confirmed = True
                            break
    except Exception as e:
        await callback_query.message.answer(f"⚠ Помилка перевірки оплати: {e}")
        await callback_query.answer()
        return

    if not payment_confirmed:
        await callback_query.message.answer(
            "⚠ Оплата ще не знайдена.\n"
            "🔄 Якщо ви щойно оплатили — зачекайте кілька секунд і натисніть 'Я оплатив' ще раз.\n"
            "💳 Якщо ще не оплатили — перейдіть за посиланням вище."
        )
        await callback_query.answer()
        return

    jitsi_link = generate_jitsi_link(psychologist_login, preferred_time)
    if not jitsi_link:
        await callback_query.message.answer("⚠ Неможливо створити посилання для зустрічі. Спробуйте пізніше.")
        await callback_query.answer()
        return

    new_request = {
        "psychologist_login": psychologist_login,
        "problem": data.get("problem", ""),
        "duration": data.get("duration", ""),
        "expectations": data.get("expectations", ""),
        "preferred_time": preferred_time,
        "client_id": user.id,
        "status": "підтверджено",
        "meet_link": jitsi_link,
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M")
    }

    requests_file = os.path.join("data", "requests.json")
    try:
        with FileLock(requests_file + ".lock"):
            all_requests = []
            if os.path.exists(requests_file):
                with open(requests_file, "r", encoding="utf-8") as f:
                    all_requests = json.load(f)
            all_requests.append(new_request)
            with open(requests_file, "w", encoding="utf-8") as f:
                json.dump(all_requests, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Помилка збереження заявки: {e}")

    try:
        approved_file = os.path.join("data", "approved_psychologists.json")
        with open(approved_file, "r", encoding="utf-8") as f:
            psychs = json.load(f)
        psych = next((p for p in psychs if p["login"] == psychologist_login), None)
        if psych and "user_id" in psych:
            await callback_query.bot.send_message(
                chat_id=psych["user_id"],
                text=(
                    f"📢 Нова підтверджена консультація!\n"
                    f"👤 Клієнт: @{user.username or user.full_name}\n"
                    f"🗓 Час: {preferred_time}\n"
                    f"🔗 Посилання: {jitsi_link}"
                )
            )
    except Exception as e:
        print(f"⚠ Не вдалося надіслати повідомлення психологу: {e}")

    await callback_query.message.answer(
        f"✅ Оплата підтверджена!\n"
        f"🗓 Ви забронювали: <b>{preferred_time}</b>\n"
        f"🔗 Посилання на консультацію: {jitsi_link}",
        parse_mode="HTML"
    )

    await state.clear()
    await callback_query.answer("✅ Консультацію підтверджено!")
