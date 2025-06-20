from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from typing import Tuple
from filelock import FileLock

import os
import json
import hmac
import hashlib
import base64
from datetime import datetime

# 🔁 Завантаження .env
load_dotenv()

# 🔧 Ініціалізація FastAPI та бота
app = FastAPI()
bot = Bot(token=os.getenv("BOT_TOKEN"))

# 📁 Шляхи до файлів
MERCHANT_SECRET_KEY = os.getenv("MERCHANT_SECRET_KEY")
PENDING_FILE = os.path.join("data", "pending_payments.json")
LOCK_FILE = PENDING_FILE + ".lock"

# 🔐 Перевірка підпису WayForPay
def verify_signature(data: dict) -> Tuple[bool, str]:
    try:
        amount = f"{float(data.get('amount')):.2f}"
        fields = [
            data.get("merchantAccount"),
            data.get("orderReference"),
            amount,
            data.get("currency"),
            data.get("authCode"),
            data.get("cardPan"),
            data.get("transactionStatus"),
            str(data.get("reasonCode"))
        ]
        sign_string = ";".join(fields)
        generated_signature = base64.b64encode(
            hmac.new(MERCHANT_SECRET_KEY.encode(), sign_string.encode(), hashlib.md5).digest()
        ).decode()

        expected = generated_signature
        actual = data.get("merchantSignature")

        print("🔐 Sign string:", sign_string)
        print("🔐 Generated signature:", expected)
        print("🔐 Actual signature:", actual)

        return expected == actual, expected
    except Exception as e:
        print("🚫 Signature error:", e)
        return False, ""

# 📥 Обробка webhook
@app.post("/webhook")
async def webhook_handler(request: Request):
    try:
        data = await request.json()
        print("📥 Webhook отримано:", json.dumps(data, indent=2, ensure_ascii=False))
        print("📬 FULL PAYLOAD:", json.dumps(data, indent=2, ensure_ascii=False))

        valid, expected_sig = verify_signature(data)
        print("🔑 Отримано:", data.get("merchantSignature"))
        print("🔑 Очікувано:", expected_sig)

        if not valid:
            print("🚫 Невірний підпис!")
            return JSONResponse(status_code=400, content={"error": "Invalid signature"})

        if data.get("transactionStatus") == "Approved":
            await mark_payment_as_paid(data.get("orderReference"))

        return JSONResponse(content={"orderReference": data.get("orderReference"), "status": "accept"})

    except Exception as e:
        print("❌ Webhook error:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})

# ✅ Оновлення статусу платежу
async def mark_payment_as_paid(reference: str):
    if not os.path.exists(PENDING_FILE):
        print("⚠️ Файл pending_payments.json не знайдено.")
        return

    updated = False
    user_id = None

    try:
        with FileLock(LOCK_FILE):
            with open(PENDING_FILE, "r", encoding="utf-8") as f:
                payments = json.load(f)

            print("📂 Поточний вміст перед оновленням:")
            for item in payments:
                print("-", item.get("orderReference"), "|", item.get("status"))

            for item in payments:
                print(f"🔍 CHECK: {item.get('orderReference')} == {reference}")
                if item.get("orderReference", "").strip() == reference.strip():
                    if item.get("status") != "paid":
                        item["status"] = "paid"
                        item["updated_at"] = datetime.utcnow().isoformat()
                        user_id = item.get("user_id")
                        updated = True
                        print(f"✅ Оновлено статус для {reference}")
                    else:
                        print(f"ℹ️ Статус вже 'paid' для {reference}")
                    break
            else:
                print(f"❌ Запис з orderReference '{reference}' не знайдено")

            if updated:
                with open(PENDING_FILE, "w", encoding="utf-8") as f:
                    json.dump(payments, f, indent=2, ensure_ascii=False)
                print("💾 Збережено оновлений файл.")

            print("🧾 Вміст після оновлення:")
            for item in payments:
                print("-", item.get("orderReference"), "|", item.get("status"))

    except Exception as e:
        print(f"❌ Помилка оновлення статусу: {e}")
        return

    # Повідомлення користувачу
    if updated and user_id:
        try:
            await bot.send_message(
                chat_id=user_id,
                text="✅ Оплату підтверджено!\nНатисніть кнопку нижче, щоб завершити бронювання.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Завершити бронювання", callback_data="pay_confirm")]
                ])
            )
            print(f"📨 Повідомлення надіслано користувачу {user_id}")
        except Exception as e:
            print(f"❌ Не вдалося надіслати повідомлення користувачу {user_id}: {e}")

# 🔄 Сторінка повернення після оплати
@app.get("/return")
async def return_page(user_id: int, ref: str):
    paid = False
    try:
        with FileLock(LOCK_FILE):
            if os.path.exists(PENDING_FILE):
                with open(PENDING_FILE, "r", encoding="utf-8") as f:
                    payments = json.load(f)
                    for item in payments:
                        if item.get("orderReference") == ref and item.get("user_id") == user_id:
                            paid = item.get("status") == "paid"
                            break
    except Exception as e:
        print("❌ Помилка читання return:", e)

    message = (
        "✅ Оплату підтверджено. Поверніться в бот." if paid else
        "❗ Оплата не підтверджена. Поверніться в бот і натисніть «Я оплатив»."
    )

    return HTMLResponse(f"""
        <html>
            <head><title>Статус оплати</title></head>
            <body style="font-family: sans-serif; text-align: center; padding-top: 60px;">
                <h2>{message}</h2>
                <p>Цю сторінку можна закрити.</p>
            </body>
        </html>
    """)