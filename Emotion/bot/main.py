import asyncio
import logging
import sys
from threading import Thread

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import BotCommand

from bot.utils.scheduler import run_affirmation_scheduler
from bot.config import BOT_TOKEN
from bot.handlers import (
    client,
    custom_calendar,
    psychologist,
    admin_approval,
    calendar,
)

# Імпорт FastAPI-додатку з webhook.py (для WayForPay)
from webhook import app as fastapi_app
import uvicorn


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        print(f"📝 Отримано оновлення:\n{event}")
        return await handler(event, data)


logging.basicConfig(level=logging.INFO, stream=sys.stdout)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.message.outer_middleware(LoggingMiddleware())
dp.callback_query.outer_middleware(LoggingMiddleware())

dp.include_router(client.router)
dp.include_router(psychologist.router)
dp.include_router(custom_calendar.router)
dp.include_router(admin_approval.router)
dp.include_router(calendar.router)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="help", description="Допомога"),
        BotCommand(command="about", description="Про бота"),
        BotCommand(command="profile", description="Мій профіль"),
        BotCommand(command="bookings", description="Мої консультації"),
        BotCommand(command="contact", description="Зв'язатися з командою"),
        BotCommand(command="manage_affirmation", description="Керувати афірмацією")
    ]
    await bot.set_my_commands(commands)


def start_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)


async def main():
    print("Bot is starting...")

    # 🧩 Видаляємо webhook (щоб Telegram не дублікував повідомлення)
    await bot.delete_webhook(drop_pending_updates=True)

    # 🚀 Запускаємо FastAPI у фоновому потоці (для WayForPay webhook)
    Thread(target=start_fastapi, daemon=True).start()

    # ⏱ Розклад афірмацій
    asyncio.create_task(run_affirmation_scheduler(bot))

    # 📋 Команди
    await set_bot_commands(bot)

    # 🤖 Запуск polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())