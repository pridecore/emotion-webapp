from aiogram import Router, F
from aiogram.types import CallbackQuery
import json
import os

router = Router()

PENDING_FILE = os.path.join("data", "pending_psychologists.json")
APPROVED_FILE = os.path.join("data", "approved_psychologists.json")

# Створити файли, якщо не існують
def ensure_files():
    for path in [PENDING_FILE, APPROVED_FILE]:
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

# ✅ Підтвердження заявки психолога
@router.callback_query(F.data.startswith("approve_"))
async def approve_request(callback: CallbackQuery):
    ensure_files()
    request_id = callback.data.replace("approve_", "")

    with open(PENDING_FILE, "r", encoding="utf-8") as f:
        pending = json.load(f)

    target = next((r for r in pending if r["request_id"] == request_id), None)

    if not target:
        await callback.message.answer("❌ Заявку не знайдено або вже опрацьовано.")
        return

    pending = [r for r in pending if r["request_id"] != request_id]
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(pending, f, indent=2, ensure_ascii=False)

    # Додати до approved
    with open(APPROVED_FILE, "r", encoding="utf-8") as f:
        approved = json.load(f)

    approved.append(target)
    with open(APPROVED_FILE, "w", encoding="utf-8") as f:
        json.dump(approved, f, indent=2, ensure_ascii=False)

    await callback.bot.send_message(
        chat_id=target["telegram_id"],
        text="🎉 Ваш профіль було підтверджено! Тепер ви можете використовувати платформу."
    )

    await callback.message.answer("✅ Заявку підтверджено.")
    await callback.answer()

# ❌ Відхилення заявки психолога
@router.callback_query(F.data.startswith("decline_"))
async def decline_request(callback: CallbackQuery):
    ensure_files()
    request_id = callback.data.replace("decline_", "")

    with open(PENDING_FILE, "r", encoding="utf-8") as f:
        pending = json.load(f)

    target = next((r for r in pending if r["request_id"] == request_id), None)

    if not target:
        await callback.message.answer("❌ Заявку не знайдено або вже опрацьовано.")
        return

    pending = [r for r in pending if r["request_id"] != request_id]
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(pending, f, indent=2, ensure_ascii=False)

    await callback.bot.send_message(
        chat_id=target["telegram_id"],
        text="❌ Вашу заявку на платформу було відхилено. Ви можете звернутись до адміністратора."
    )

    await callback.message.answer("🚫 Заявку відхилено.")
    await callback.answer()
