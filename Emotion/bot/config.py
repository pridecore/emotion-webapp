import os
from dotenv import load_dotenv

from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)


# 📌 ID головного психолога (обробляє запити з категорії "Інше")
MAIN_PSYCHOLOGIST_ID = 7761542233
