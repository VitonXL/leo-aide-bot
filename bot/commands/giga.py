# bot/commands/giga.py

from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.giga import send_to_giga
from bot.database import check_premium, log_action
from datetime import datetime
import os

# Храним количество запросов (позже — в БД)
user_requests = {}

async def giga_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Проверяем, не команда ли это
    if text.startswith('/'):
        return

    # Проверяем, есть ли команда /giga
    if text.lower().startswith('giga') or 'giga' in text.lower():
        # Проверяем премиум
        if not check_premium(user_id):
            await update.message.reply_text(
                "💎 Чтобы пользоваться GigaChat, нужен премиум-аккаунт.\n"
                "Используй /premium, чтобы приобрести."
            )
            return

        # Проверяем лимит запросов
        today = datetime.now().date()
        if user_id not in user_requests:
            user_requests[user_id] = {'date': today, 'count': 0}

        user_data = user_requests[user_id]
        if user_data['date'] != today:
            user_data['date'] = today
            user_data['count'] = 0

        if user_data['count'] >= 10:
            await update.message.reply_text("❗ Лимит запросов GigaChat — 10 в день. Попробуйте завтра.")
            return

        # Увеличиваем счётчик
        user_data['count'] += 1

        # Отправляем в GigaChat
        await update.message.reply_text("🧠 Думаю...")
        response = send_to_giga(text)
        await update.message.reply_text(response)

        # Логируем
        log_action(user_id, "giga_query", text[:50])
