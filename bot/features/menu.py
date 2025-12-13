# bot/features/menu.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler


# --- Клавиатуры ---
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("👤 Личный кабинет", callback_data="menu_profile")],
        [InlineKeyboardButton("💎 Премиум функционал", callback_data="menu_premium")],
        [InlineKeyboardButton("🔧 Функционал", callback_data="menu_features")],
        [InlineKeyboardButton("🎮 Игры", callback_data="menu_games")],
        [InlineKeyboardButton("🛡 Антивирус", callback_data="menu_antivirus")],
        [InlineKeyboardButton("🌐 Обход блокировок", callback_data="menu_unlock")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="menu_settings")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_profile_menu():
    keyboard = [
        [InlineKeyboardButton("💳 Покупка премиума", callback_data="profile_premium")],
        [InlineKeyboardButton("🤝 Реферальная система", callback_data="profile_referral")],
        [InlineKeyboardButton("⚙️ Настройки аккаунта", callback_data="profile_settings")],
        [InlineKeyboardButton("ℹ️ Информация об аккаунте", callback_data="profile_info")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_features_menu():
    keyboard = [
        [InlineKeyboardButton("🌤 Погода", callback_data="features_weather")],
        [InlineKeyboardButton("💱 Курсы валют", callback_data="features_currency")],
        [InlineKeyboardButton("🕰 Напоминания", callback_data="features_reminders")],
        [InlineKeyboardButton("🔔 Отслеживание подписок", callback_data="features_subscriptions")],
        [InlineKeyboardButton("🎮 Игры Telegram", callback_data="features_telegram_games")],
        [InlineKeyboardButton("📰 Новости", callback_data="features_news")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_premium_menu():
    keyboard = [
        [InlineKeyboardButton("🤖 GigaChat", callback_data="premium_gigachat")],
        [InlineKeyboardButton("🎮 Кастомные игры", callback_data="premium_games")],
        [InlineKeyboardButton("🎬 Подбор фильмов", callback_data="premium_movies")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_settings_menu():
    keyboard = [
        [InlineKeyboardButton("🔔 Уведомления", callback_data="settings_notifications")],
        [InlineKeyboardButton("🌐 Язык", callback_data="settings_language")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


# --- Обработчики ---
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *Главное меню*\n\nВыбери раздел:",
        reply_markup=get_main_menu(),
        parse_mode='Markdown'
    )


async def handle_menu_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # --- Главное меню ---
    if data == "menu_main":
        await query.edit_message_text("📌 *Главное меню*", reply_markup=get_main_menu(), parse_mode='Markdown')

    # --- Личный кабинет ---
    elif data == "menu_profile":
        await query.edit_message_text(
            "👤 *Личный кабинет*\n\nВыбери действие:",
            reply_markup=get_profile_menu(),
            parse_mode='Markdown'
        )

    elif data == "profile_premium":
        await query.edit_message_text(
            "💳 *Покупка премиума*\n\n"
            "🔹 Тариф: 199 ₽/мес\n"
            "🔹 Преимущества: все функции без ограничений\n"
            "🔹 Оплата: Telegram Stars / Карта\n\n"
            "🛠 Платёжная система в разработке...",
            reply_markup=get_profile_menu(),
            parse_mode='Markdown'
        )

    elif data == "profile_referral":
        await query.edit_message_text(
            "🤝 *Реферальная система*\n\n"
            "Приглашай друзей и получай бонусы!\n\n"
            "🔗 Твоя реферальная ссылка:\n"
            "`https://t.me/Leo_aide_bot?start=ref123`\n\n"
            "🎁 За каждого друга: +3 дня премиума\n\n"
            "🛠 Система в разработке...",
            reply_markup=get_profile_menu(),
            parse_mode='Markdown'
        )

    elif data == "profile_settings":
        await query.edit_message_text(
            "⚙️ *Настройки аккаунта*\n\n"
            "Доступно:\n"
            "• Смена имени\n"
            "• Привязка email\n"
            "• Уведомления\n"
            "• Конфиденциальность\n\n"
            "🛠 Настройки скоро будут доступны",
            reply_markup=get_profile_menu(),
            parse_mode='Markdown'
        )

    elif data == "profile_info":
        await query.edit_message_text(
            "ℹ️ *Информация об аккаунте*\n\n"
            "• ID: 123456789\n"
            "• Подписка: нет\n"
            "• Рефералов: 0\n"
            "• Дата регистрации: 2025-04-05\n"
            "• Язык: русский\n\n"
            "🛠 Данные обновляются позже",
            reply_markup=get_profile_menu(),
            parse_mode='Markdown'
        )

    # --- Функционал ---
    elif data == "menu_features":
        await query.edit_message_text(
            "🔧 *Функционал*\n\nВыбери инструмент:",
            reply_markup=get_features_menu(),
            parse_mode='Markdown'
        )

    elif data == "features_weather":
        await query.edit_message_text(
            "🌤 *Погода*\n\n"
            "Введите город: /weather Москва\n\n"
            "🛠 Функция в разработке...",
            reply_markup=get_features_menu(),
            parse_mode='Markdown'
        )

    elif data == "features_currency":
        await query.edit_message_text(
            "💱 *Курсы валют*\n\n"
            "Поддерживаемые: USD, EUR, GBP, CNY\n\n"
            "Используй: /currency USD\n\n"
            "🛠 В разработке...",
            reply_markup=get_features_menu(),
            parse_mode='Markdown'
        )

    elif data == "features_reminders":
        await query.edit_message_text(
            "🕰 *Напоминания*\n\n"
            "Создай напоминание:\n"
            "`/remind 30 выпить воды`\n\n"
            "🛠 Реализуется...",
            reply_markup=get_features_menu(),
            parse_mode='Markdown'
        )

    elif data == "features_subscriptions":
        await query.edit_message_text(
            "🔔 *Отслеживание подписок*\n\n"
            "Список активных:\n"
            "• YouTube Premium\n"
            • Spotify\n
            • Telegram Premium\n\n"
            "🔔 Уведомление за 3 дня\n\n"
            "🛠 В разработке...",
            reply_markup=get_features_menu(),
            parse_mode='Markdown'
        )

    elif data == "features_telegram_games":
        await query.edit_message_text(
            "🎮 *Игры Telegram*\n\n"
            "Запустить игру:\n"
            "• @gamee\n"
            "• @fork_delta_bot\n\n"
            "🛠 Подбор лучших игр скоро...",
            reply_markup=get_features_menu(),
            parse_mode='Markdown'
        )

    elif data == "features_news":
        await query.edit_message_text(
            "📰 *Новости*\n\n"
            "Темы:\n"
            "• Технологии\n"
            "• Финансы\n"
            "• Telegram-обновления\n\n"
            "🛠 Лента новостей в разработке...",
            reply_markup=get_features_menu(),
            parse_mode='Markdown'
        )

    # --- Премиум функционал ---
    elif data == "menu_premium":
        await query.edit_message_text(
            "💎 *Премиум функционал*\n\nВыбери инструмент:",
            reply_markup=get_premium_menu(),
            parse_mode='Markdown'
        )

    elif data == "premium_gigachat":
        await query.edit_message_text(
            "🤖 *GigaChat*\n\n"
            "Задай любой вопрос:\n"
            "`/giga Расскажи про ИИ`"
            "\n\n"
            "🚀 Мощный ИИ от Сбера\n\n"
            "🛠 Интеграция в процессе...",
            reply_markup=get_premium_menu(),
            parse_mode='Markdown'
        )

    elif data == "premium_games":
        await query.edit_message_text(
            "🎮 *Кастомные игры*\n\n"
            "Доступно:\n"
            "• Крестики-нолики с ИИ\n"
            "• Викторина по фильмам\n"
            "• Угадай мем\n\n"
            "🛠 Игры разрабатываются...",
            reply_markup=get_premium_menu(),
            parse_mode='Markdown'
        )

    elif data == "premium_movies":
        await query.edit_message_text(
            "🎬 *Подбор фильмов*\n\n"
            "Укажи жанр:\n"
            "`/movie комедия`\n\n"
            "С учётом твоих предпочтений\n\n"
            "🛠 Рекомендации скоро...",
            reply_markup=get_premium_menu(),
            parse_mode='Markdown'
        )

    # --- Настройки ---
    elif data == "menu_settings":
        await query.edit_message_text(
            "⚙️ *Настройки*\n\nВыбери параметр:",
            reply_markup=get_settings_menu(),
            parse_mode='Markdown'
        )

    elif data == "settings_notifications":
        await query.edit_message_text(
            "🔔 *Уведомления*\n\n"
            "Текущий статус: выключены\n\n"
            "🛠 Настройка скоро будет доступна",
            reply_markup=get_settings_menu(),
            parse_mode='Markdown'
        )

    elif data == "settings_language":
        await query.edit_message_text(
            "🌐 *Язык*\n\n"
            "Доступные языки:\n"
            "• Русский\n"
            "• English\n\n"
            "🛠 Переключение в разработке",
            reply_markup=get_settings_menu(),
            parse_mode='Markdown'
        )


# --- Регистрация ---
def setup(application):
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(
        CallbackQueryHandler(handle_menu_callbacks, pattern=r"^menu_|^profile_|^features_|^premium_|^settings_")
    )
