# bot/features/start.py

from telegram import Update, BotCommand
from telegram.ext import ContextTypes, CommandHandler


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Установим только существующие команды
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("help", "Показать помощь"),
        BotCommand("menu", "Открыть главное меню"),
    ]
    await context.bot.set_my_commands(commands)

    # Клавиатура
    keyboard = [
        ["/help"],
        ["/menu"]
    ]

    await update.message.reply_text(
        "👋 Привет! Я — *Лео*, твой помощник.\n"
        "Пока я в процессе обучения, но уже могу помочь с базовыми задачами.",
        reply_markup={"keyboard": keyboard, "resize_keyboard": True},
        parse_mode='Markdown'
    )


def setup(application):
    application.add_handler(CommandHandler("start", start_command))
