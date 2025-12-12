# bot/commands/start.py

from telegram import Update
from telegram.ext import ContextTypes
from bot.database import add_user, get_user, add_referral, log_action

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    referrer_id = None

    if context.args:
        try:
            referrer_id = int(context.args[0])
            if referrer_id == user.id:
                referrer_id = None  # нельзя сам себя пригласить
        except:
            pass

    # Добавляем пользователя
    add_user(user.id, user.username, user.first_name, user.last_name, referred_by=referrer_id)
    log_action(user.id, "start", referrer_id)

    # Если есть пригласивший — добавляем в систему
    if referrer_id:
        # Определим уровень
        referrer = get_user(referrer_id)
        if referrer and referrer['referred_by']:
            referrer2 = get_user(referrer['referred_by'])
            if referrer2 and referrer2['referred_by']:
                level = 3
            else:
                level = 2
        else:
            level = 1

        add_referral(referrer_id, user.id, level=level)

    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n"
        "Я — Лео, ваш личный помощник.\n"
        "Используй /help, чтобы посмотреть команды.\n\n"
        "💡 Приглашайте друзей через /referral и получайте премиум бесплатно!"
    )
