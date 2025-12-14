# bot/main.py

from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from features.menu import menu_command, handle_menu_buttons  # ← импорт
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "Привет! 👋\n\n"
        "Нажми /menu, чтобы открыть главное меню.",
        reply_markup=None
    )

async def post_init(application):
    await application.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="🌐 Панель",
            web_app=WebAppInfo(url="https://web-production-b74ea.up.railway.app")
        )
    )

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))  # ← добавляем /menu
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))  # ← обработка кнопок

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
