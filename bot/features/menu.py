# bot/features/menu.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler


# --- Генерация клавиатур ---
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="menu_help")],
        [InlineKeyboardButton("👤 Мой профиль", callback_data="menu_profile")],
        [InlineKeyboardButton("🛠 Настройки", callback_data="nav_settings")],
        [InlineKeyboardButton("🗑 Закрыть", callback_data="menu_close")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_settings_menu():
    keyboard = [
        [InlineKeyboardButton("🔔 Уведомления", callback_data="nav_notifications")],
        [InlineKeyboardButton("🌐 Язык", callback_data="nav_language")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_notifications_menu():
    keyboard = [
        [InlineKeyboardButton("✅ Включить", callback_data="action_notify_on")],
        [InlineKeyboardButton("❌ Выключить", callback_data="action_notify_off")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="nav_settings")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_language_menu():
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="nav_settings")],
    ]
    return InlineKeyboardMarkup(keyboard)


# --- Основные обработчики ---
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *Главное меню*\n\nВыбери раздел:",
        reply_markup=get_main_menu(),
        parse_mode='Markdown'
    )


async def handle_menu_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    data = query.data

    # --- Главное меню ---
    if data == "menu_main":
        await query.edit_message_text("📌 *Главное меню*", reply_markup=get_main_menu(), parse_mode='Markdown')

    elif data == "menu_help":
        text = (
            "🔧 *Помощь*\n\n"
            "Я — *Лео*, твой личный помощник.\n\n"
            "Используй меню для навигации.\n"
            "Скоро появятся напоминания и задачи!"
        )
        await query.edit_message_text(text, reply_markup=get_main_menu(), parse_mode='Markdown')

    elif data == "menu_profile":
        text = (
            "📋 *Ваш профиль:*\n"
            f"• Имя: {user.full_name}\n"
            f"• ID: {user.id}\n"
            f"• Username: @{user.username or 'не задан'}"
        )
        await query.edit_message_text(text, reply_markup=get_main_menu(), parse_mode='Markdown')

    # --- Настройки ---
    elif data == "nav_settings":
        text = "🛠 *Настройки*\n\nВыбери категорию:"
        await query.edit_message_text(text, reply_markup=get_settings_menu(), parse_mode='Markdown')

    # --- Уведомления ---
    elif data == "nav_notifications":
        text = "🔔 *Управление уведомлениями*"
        await query.edit_message_text(text, reply_markup=get_notifications_menu(), parse_mode='Markdown')

    elif data == "action_notify_on":
        await query.edit_message_text(
            "✅ Уведомления включены",
            reply_markup=get_notifications_menu(),
            parse_mode='Markdown'
        )
        # Здесь можно сохранить в context.user_data или БД
        context.user_data["notifications"] = True

    elif data == "action_notify_off":
        await query.edit_message_text(
            "❌ Уведомления выключены",
            reply_markup=get_notifications_menu(),
            parse_mode='Markdown'
        )
        context.user_data["notifications"] = False

    # --- Язык ---
    elif data == "nav_language":
        text = "🌐 Выбери язык интерфейса:"
        await query.edit_message_text(text, reply_markup=get_language_menu(), parse_mode='Markdown')

    elif data == "lang_ru":
        await query.edit_message_text("🇷🇺 Язык установлен: Русский", reply_markup=get_language_menu(), parse_mode='Markdown')
        context.user_data["language"] = "ru"

    elif data == "lang_en":
        await query.edit_message_text("🇬🇧 Language set to English", reply_markup=get_language_menu(), parse_mode='Markdown')
        context.user_data["language"] = "en"

    # --- Закрыть ---
    elif data == "menu_close":
        await query.delete_message()


# --- Регистрация ---
def setup(application):
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(handle_menu_callbacks, pattern=r"^menu_|^nav_|^action_|^lang_"))
