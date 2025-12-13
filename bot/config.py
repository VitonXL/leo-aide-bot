# bot/config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")  # Будет от Railway
WEBHOOK_URL = os.getenv("WEBHOOK_URL")   # Если используешь webhook
PORT = int(os.getenv("PORT", 8000))
