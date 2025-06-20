import hmac
import hashlib
import json
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv
import requests
from filelock import FileLock

# 🌐 Завантаження .env
load_dotenv()

MERCHANT_ACCOUNT = os.getenv("MERCHANT_ACCOUNT")
MERCHANT_DOMAIN = os.getenv("MERCHANT_DOMAIN")
MERCHANT_SECRET_KEY = os.getenv("MERCHANT_SECRET_KEY")
SERVICE_URL = os.getenv("SERVICE_URL")   # Webhook
RETURN_URL = os.getenv("RETURN_URL")     # Redirect
API_URL = "https://api.wayforpay.com/api"

PENDING_FILE = os.path.join("data", "pending_payments.json")
LOCK_FILE = PENDING_FILE + ".lock"


# 🔐 Генерація підпису
def generate_signature(keys: list) -> str:
    sign_str = ';'.join(str(k) for k in keys)
    signature = hmac.new(
        MERCHANT_SECRET_KEY.encode("utf-8"),
        sign_str.encode("utf-8"),
        hashlib.md5
    ).hexdigest()
    return signature


# 💾 Додавання запису до pending_payments.json
def save_pending_payment(user_id: int, order_reference: str, amount: float):
    new_entry = {
        "user_id": user_id,
        "orderReference": order_reference,
        "amount": amount,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }

    try:
        with FileLock(LOCK_FILE, timeout=3):
            if os.path.exists(PENDING_FILE):
                with open(PENDING_FILE, "r", encoding="utf-8") as f:
                    try:
                        payments = json.load(f)
                    except json.JSONDecodeError:
                        payments = []
            else:
                payments = []

            # 🔁 Уникнення дублів
            if not any(p["orderReference"] == order_reference for p in payments):
                payments.append(new_entry)
                with open(PENDING_FILE, "w", encoding="utf-8") as f:
                    json.dump(payments, f, indent=2, ensure_ascii=False)
                print(f"💾 Збережено новий запис: {order_reference}")
            else:
                print(f"⚠️ Запис уже існує: {order_reference}")

    except Exception as e:
        print(f"❌ Помилка збереження платежу: {e}")


# 📦 Створення інвойсу через WayForPay API
def create_invoice(user_id: int, amount: float, product_name: str):
    order_reference = f"{user_id}_{uuid.uuid4().hex[:8]}"
    order_date = int(datetime.now().timestamp())

    payload = {
        "transactionType": "CREATE_INVOICE",
        "merchantAccount": MERCHANT_ACCOUNT,
        "merchantDomainName": MERCHANT_DOMAIN,
        "orderReference": order_reference,
        "orderDate": order_date,
        "amount": f"{amount:.2f}",
        "currency": "UAH",
        "productName": [product_name],
        "productPrice": [f"{amount:.2f}"],
        "productCount": [1],
        "clientFirstName": "User",
        "clientLastName": str(user_id),
        "serviceUrl": SERVICE_URL,
        "returnUrl": RETURN_URL,
        "apiVersion": 1
    }

    signature_data = [
        payload["merchantAccount"],
        payload["merchantDomainName"],
        payload["orderReference"],
        str(payload["orderDate"]),
        payload["amount"],
        payload["currency"],
        payload["productName"][0],
        str(payload["productCount"][0]),
        payload["amount"]
    ]
    payload["merchantSignature"] = generate_signature(signature_data)

    try:
        response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
        resp_data = response.json()

        if resp_data.get("reasonCode") == 1100:
            invoice_url = resp_data.get("invoiceUrl")
            save_pending_payment(user_id, order_reference, amount)
            print(f"✅ Інвойс створено: {invoice_url}")
            return invoice_url, order_reference
        else:
            print(f"❌ WayForPay помилка [{resp_data.get('reasonCode')}]: {resp_data.get('reason')}")
            return None, None

    except Exception as e:
        print(f"❌ Не вдалося створити інвойс: {e}")
        return None, None