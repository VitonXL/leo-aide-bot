# bot/commands/webapp.py

from telegram import Update, KeyboardButton, WebAppInfo, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def profile_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    web_app_url = "https://leo-helper.up.railway.app/app"
    
    keyboard = [[KeyboardButton("📱 Открыть профиль", web_app=WebAppInfo(url=web_app_url))]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👇 Нажмите кнопку, чтобы открыть ваш профиль",
        reply_markup=reply_markup
    )
