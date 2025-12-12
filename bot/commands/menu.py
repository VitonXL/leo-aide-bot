# bot/commands/menu.py

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler
from bot.database import get_user, check_premium

# Основное меню
def get_main_menu(premium: bool):
    buttons = [
        [KeyboardButton("🌤 Погода"), KeyboardButton("💵 Курсы валют")],
        [KeyboardButton("⏰ Напоминания"), KeyboardButton("🛡 Антивирус")],
        [KeyboardButton("🕒 Время"), KeyboardButton("🤖 GigaChat")]
    ]
    
    if premium:
        buttons.append([KeyboardButton("🎬 Фильмы"), KeyboardButton("📊 Статистика")])
    
    buttons.append([KeyboardButton("💎 Премиум"), KeyboardButton("👥 Рефералы")])
    buttons.append([KeyboardButton("🎮 Игры"), KeyboardButton("🛠 Настройки")])
    
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)

async def start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Открывает главное меню (вызывается через /start или /menu)"""
    user = update.effective_user
    db_user = get_user(user.id)
    
    if not db_user:
        from bot.commands.start import start
        return await start(update, context)
    
    premium = check_premium(user.id)
    is_admin = user.id in map(int, os.getenv("ADMIN_IDS", "").split(",")) if os.getenv("ADMIN_IDS") else False

    welcome_text = (
        f"🏠 Добро пожаловать, {user.first_name}!\n\n"
        f"{'💎 У вас активен премиум-аккаунт!' if premium else '🚀 Улучшите аккаунт — станьте премиум!'}"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu(premium)
    )

# Обработчик нажатий на кнопки
async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    premium = check_premium(user_id)
    
    # Премиум
    if text == "💎 Премиум":
        from bot.commands.premium import premium_command
        return await premium_command(update, context)
    
    # Погода
    elif text == "🌤 Погода":
        from bot.commands.weather import weather_command
        return await weather_command(update, context)
    
    # Курсы валют
    elif text == "💵 Курсы валют":
        from bot.commands.currency import currency_command
        await currency_command(update, context)
    
    # Напоминания
    elif text == "⏰ Напоминания":
        from bot.commands.reminders import show_reminders
        await show_reminders(update, context)
    
    # Антивирус
    elif text == "🛡 Антивирус":
        from bot.commands.antivirus import antivirus_info
        await antivirus_info(update, context)
    
    # Время
    elif text == "🕒 Время":
        from bot.commands.time import time_command
        await time_command(update, context)
    
    # GigaChat
    elif text == "🤖 GigaChat":
        await update.message.reply_text("🧠 Напишите что-нибудь — и я отвечу!")
        # GigaChat ловится через MessageHandler
    
    # Фильмы (только премиум)
    elif text == "🎬 Фильмы":
        if not premium:
            await update.message.reply_text("❌ Эта функция доступна только премиум-пользователям.")
        else:
            await update.message.reply_text("🎬 *Подбор фильмов*\n\nВ разработке...")
            # Позже подключим Kinopoisk
        return
    
    # Рефералы
    elif text == "👥 Рефералы":
        from bot.commands.referral import referral_command
        await referral_command(update, context)
    
    # Игры
    elif text == "🎮 Игры":
        from bot.commands.games import games_menu
        await games_menu(update, context)
    
    # Настройки
    elif text == "🛠 Настройки":
        await update.message.reply_text(
            "🛠 *Настройки*\n\n"
            "📍 Часовой пояс\n"
            "🔔 Уведомления\n"
            "🌐 Язык\n"
            "🗑 Очистить данные\n\n"
            "В разработке...",
            parse_mode='Markdown'
        )
    
    # Статистика (только премиум)
    elif text == "📊 Статистика":
        if not premium:
            await update.message.reply_text("❌ Доступно только премиум-пользователям.")
        else:
            from bot.database import get_user_count, get_premium_count
            total = get_user_count()
            premium_count = get_premium_count()
            await update.message.reply_text(
                f"📈 *Ваша статистика*\n\n"
                f"👥 Всего пользователей: {total}\n"
                f"💎 Премиум: {premium_count}",
                parse_mode='Markdown'
            )
