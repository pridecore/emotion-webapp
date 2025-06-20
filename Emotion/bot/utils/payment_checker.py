import asyncio
import os
import json
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from filelock import FileLock

PENDING_FILE = os.path.join("data", "pending_payments.json")
LOCK_FILE = PENDING_FILE + ".lock"

async def check_payment_after_delay(chat_id: int, order_ref: str, bot: Bot, delay_seconds: int = 60):
    """
    Через delay_seconds секунд перевіряє статус платежу в pending_payments.json.
    Якщо оплата підтверджена — повідомляє.
    Якщо ні — надсилає кнопку "Я оплатив".
    """
    print(f"[{datetime.now()}] ⏳ Очікуємо оплату для: {order_ref}")
    await bot.send_message(chat_id, "🔄 Очікуємо підтвердження оплати…")

    await asyncio.sleep(delay_seconds)

    if not os.path.exists(PENDING_FILE):
        print(f"[{datetime.now()}] ⚠️ Файл не знайдено: {PENDING_FILE}")
        await bot.send_message(chat_id, "⚠️ Помилка: файл з платежами не знайдено.")
        return

    try:
        with FileLock(LOCK_FILE, timeout=5):
            with open(PENDING_FILE, "r", encoding="utf-8") as f:
                try:
                    payments = json.load(f)
                except json.JSONDecodeError:
                    print(f"[{datetime.now()}] ❌ JSON-файл пошкоджено або порожній")
                    payments = []

        # 🔎 Перевірка потрібного платежу
        for item in payments:
            ref = item.get("orderReference")
            status = item.get("status")
            print(f"[{datetime.now()}] 🔍 Перевірка: {ref} - {status}")

            if ref == order_ref:
                if status == "paid":
                    print(f"[{datetime.now()}] ✅ Оплату підтверджено: {order_ref}")
                    await bot.send_message(chat_id, "✅ Оплату підтверджено! Дякуємо за звернення.")
                    return
                else:
                    break  # знайдено, але ще не оплачено

        # ❌ Якщо статус не "paid" або запис не знайдено
        print(f"[{datetime.now()}] ❌ Оплату не знайдено: {order_ref}")
        confirm_button = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я оплатив", callback_data="pay_confirm")]
        ])
        await bot.send_message(
            chat_id,
            "❗ Ми не знайшли підтвердження оплати.\n"
            "Якщо ви вже здійснили платіж — натисніть кнопку нижче для повторної перевірки.",
            reply_markup=confirm_button
        )

    except Exception as e:
        print(f"[{datetime.now()}] ❌ Помилка при перевірці платежу: {e}")
        await bot.send_message(chat_id, f"⚠️ Сталася помилка при перевірці платежу.")