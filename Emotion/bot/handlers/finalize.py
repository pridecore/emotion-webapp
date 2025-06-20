import os
import json
from datetime import datetime
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from bot.handlers.psychologist import pending_confirmations


async def finalize_consultation_request(message: Message, state: FSMContext):
    data = await state.get_data()

    file_path = os.path.join("data", "requests.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    else:
        all_data = []

    all_data.append({
        "psychologist_id": data["psychologist_id"],
        "problem": data["problem"],
        "duration": data["duration"],
        "expectations": data["expectations"],
        "preferred_time": data["preferred_time"],
        "client_id": message.from_user.id,
        "status": "новий",
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M")
    })

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    summary = (
        f"🆕 <b>Новий запит від клієнта</b>\n\n"
        f"🔍 <b>Проблема:</b> {data['problem']}\n"
        f"⏳ <b>Тривалість:</b> {data['duration']}\n"
        f"🎯 <b>Очікування:</b> {data['expectations']}\n"
        f"🕒 <b>Зручний час:</b> {data['preferred_time']}\n\n"
        f"📩 <i>Відповідайте клієнту або підтвердіть консультацію нижче.</i>"
    )

    button = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Підтвердити", callback_data=f"confirm_{data['psychologist_id']}"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data=f"cancel_{data['psychologist_id']}")
        ]
    ])

    pending_confirmations[data["psychologist_id"]] = message.from_user.id

    try:
        await message.bot.send_message(
            chat_id=int(data["psychologist_id"]),
            text=summary,
            reply_markup=button,
            parse_mode="HTML"
        )
        await message.answer("✅ Ваш запит передано психологу. Очікуйте відповідь!")
    except Exception:
        await message.answer("⚠️ Помилка при надсиланні психологу. Спробуйте пізніше.")

    await state.clear()