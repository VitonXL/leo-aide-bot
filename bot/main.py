# bot/main.py

import os
from telegram import Update, MenuButtonWebApp, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# Импортируем наше меню
from features.menu import setup as setup_menu

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = "https://web-production-b74ea.up.railway.app"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "Привет! 👋\n\n"
        "Нажми /menu, чтобы открыть меню, или используй кнопку в углу (≡).",
        reply_markup=None
    )

async def post_init(application):
    # Кнопка в меню (≡)
    await application.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="🌐 Панель",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    )

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # Подключаем меню
    setup_menu(app)

    # Команда /start
    app.add_handler(CommandHandler("start", start))

    print("🚀 Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
