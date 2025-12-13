# bot/main.py

import os
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        text=f"Привет, <b>{user.first_name}</b>! 👋\n\n"
             f"Открой панель управления прямо внутри Telegram.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(
                text="📱 Открыть Mini App",
                web_app=WebAppInfo(url="https://web-production-b74ea.up.railway.app")
            )]],
            resize_keyboard=True
        )
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
