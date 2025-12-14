# bot/features/referrals.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler

# ✅ Абсолютный импорт
from database import register_referral, get_referral_stats


async def cmd_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    pool = update.get_bot().bot.db_pool

    referred = await get_referral_stats(pool, user_id)
    link = f"https://t.me/your_bot?start=ref{user_id}"

    keyboard = [[InlineKeyboardButton("📤 Поделиться", url=f"https://t.me/share/url?url={link}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"""
👥 <b>Реферальная система</b>

🔗 Ваша ссылка:
<code>{link}</code>

📬 Приглашено: <b>{referred}</b> друзей

🎁 За каждого — бонус!
🚀 Делитесь и получайте награды!
    """
    await update.message.reply_html(text, reply_markup=reply_markup)


def setup_referral_handlers(app):
    app.add_handler(CommandHandler("referral", cmd_referral))
