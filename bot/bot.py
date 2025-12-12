# bot/bot.py

import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from datetime import time

# Команды
from bot.commands.start import start
from bot.commands.premium import premium_command
from bot.commands.referral import referral_command
from bot.commands.weather import weather_command, weather_callback
from bot.commands.currency import currency_command
from bot.commands.reminders import set_reminder, reminder_callback, handle_text_input, show_reminders
from bot.commands.antivirus import virus_check, antivirus_info
from bot.commands.time import time_command, time_callback
from bot.commands.menu import start_menu, handle_menu_buttons
from bot.commands.webapp import profile_command
from bot.commands.admin import register_admin_handlers
from bot.commands.broadcast import broadcast_menu, broadcast_callback, handle_broadcast_message, cancel_broadcast
from bot.commands.subscriptions import (
    subs_command,
    add_sub_start,
    add_sub_name,
    add_sub_price,
    add_sub_date,
    add_sub_period,
    manage_subs,
    delete_sub,
    back_to_subs,
    check_due_subscriptions
)

# GigaChat
from bot.utils.giga import handle_giga_request

# Глобальные переменные
application = None

# Состояния для подписок
ADD_NAME, ADD_PRICE, ADD_DATE, ADD_PERIOD = range(4)

def bot_main():
    global application
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Основные команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", start_menu))
    application.add_handler(CommandHandler("premium", premium_command))
    application.add_handler(CommandHandler("referrals", referral_command))
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(CommandHandler("currency", currency_command))
    application.add_handler(CommandHandler("reminders", show_reminders))
    application.add_handler(CommandHandler("antivirus", antivirus_info))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("subscriptions", subs_command))
    application.add_handler(CommandHandler("subs", subs_command))

    # Callback-обработчики
    application.add_handler(CallbackQueryHandler(weather_callback, pattern="^weather_"))
    application.add_handler(CallbackQueryHandler(weather_callback, pattern="^delete_city_"))
    application.add_handler(CallbackQueryHandler(weather_callback, pattern="^weather_back$"))
    application.add_handler(CallbackQueryHandler(time_callback))
    application.add_handler(CallbackQueryHandler(reminder_callback, pattern="^reminder_"))
    application.add_handler(CallbackQueryHandler(reminder_callback, pattern="^delay_"))
    application.add_handler(CallbackQueryHandler(broadcast_callback, pattern="^broadcast_"))
    application.add_handler(CallbackQueryHandler(broadcast_callback, pattern="^target_"))
    application.add_handler(CallbackQueryHandler(broadcast_callback, pattern="^when_"))
    application.add_handler(CallbackQueryHandler(cancel_broadcast, pattern="^cancel_bcast_"))
    application.add_handler(CallbackQueryHandler(manage_subs, pattern="^manage_subs$"))
    application.add_handler(CallbackQueryHandler(delete_sub, pattern="^del_sub_"))
    application.add_handler(CallbackQueryHandler(back_to_subs, pattern="^back_to_subs$"))

    # Подписки: диалог
    add_sub_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_sub_start, pattern="^add_sub_start$")],
        states={
            ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_sub_name)],
            ADD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_sub_price)],
            ADD_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_sub_date)],
            ADD_PERIOD: [CallbackQueryHandler(add_sub_period, pattern="^period_")]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: u.message.reply_text("Отменено"))]
    )
    application.add_handler(add_sub_conv)

    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.Document.ALL | filters.URL, virus_check))
    application.add_handler(MessageHandler(filters.PHOTO, virus_check))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_giga_request))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))

    # Админка
    register_admin_handlers(application)

    # Планировщик
    application.job_queue.run_daily(check_due_subscriptions, time=time(hour=9, minute=0, second=0))

    print("🚀 Бот запущен")
