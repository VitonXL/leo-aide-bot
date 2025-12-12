# bot/commands/weather.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
import requests
import os
from bot.database import get_user, check_premium, log_action

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

# Словарь для временного хранения (позже — в БД)
user_city_input = {}  # user_id: {'state': 'waiting_city', 'action': 'add_city'}


async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await update.message.reply_text("Сначала начните бота: /start")
        return

    # Проверим, что хочет пользователь
    if context.args:
        city = " ".join(context.args)
        await _send_weather(update, context, city)
        return

    # Получаем сохранённые города
    cities = _get_saved_cities(user_id)
    premium = check_premium(user_id)

    # Клавиатура
    keyboard = []

    if cities:
        for city in cities:
            keyboard.append([InlineKeyboardButton(f"📍 {city}", callback_data=f"weather_{city}")])
        keyboard.append([InlineKeyboardButton("➕ Добавить город", callback_data="weather_add_city")])
    else:
        keyboard.append([InlineKeyboardButton("➕ Добавить первый город", callback_data="weather_add_city")])

    # Премиум-функция
    if premium:
        keyboard.append([InlineKeyboardButton("🗑️ Управление городами", callback_data="weather_manage_cities")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = "🌤️ *Погода*\n\n"
    if cities:
        msg += "Нажмите на город, чтобы посмотреть погоду.\n"
    else:
        msg += "У вас пока нет сохранённых городов."

    if not premium:
        msg += "\n\n💎 Станьте премиум-пользователем, чтобы добавить до 5 городов!"

    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')
    log_action(user_id, "weather_open")


async def weather_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data == "weather_add_city":
        await query.message.reply_text("Введите название города:")
        user_city_input[user_id] = {'state': 'waiting_city', 'action': 'add_city'}
        await query.answer()

    elif data.startswith("weather_") and "_" in data:
        city = data.split("_", 1)[1]
        if city != "add_city" and city != "manage_cities":
            await _send_weather(query, context, city)
            await query.answer()

    elif data == "weather_manage_cities":
        cities = _get_saved_cities(user_id)
        if not cities:
            await query.message.reply_text("У вас нет сохранённых городов.")
            await query.answer()
            return

        keyboard = [
            [InlineKeyboardButton(f"🗑️ Удалить {city}", callback_data=f"delete_city_{city}")]
            for city in cities
        ]
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="weather_back")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text("📂 Управление городами:", reply_markup=reply_markup)
        await query.answer()

    elif data.startswith("delete_city_"):
        city = data.replace("delete_city_", "")
        _remove_city(user_id, city)
        await query.message.reply_text(f"✅ Город *{city}* удалён.", parse_mode='Markdown')
        await query.answer()

    elif data == "weather_back":
        # Вернуться к основному меню
        await weather_command(update, context)
        await query.delete_message()
        await query.answer()


async def _send_weather(sender, context: ContextTypes.DEFAULT_TYPE, city: str):
    """Отправить погоду для города"""
    user_id = sender.from_user.id
    url = f"{WEATHER_URL}?q={city}&appid={WEATHER_API_KEY}&lang=ru&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind = data['wind']['speed']
            desc = data['weather'][0]['description'].capitalize()

            emoji = {
                'ясно': '☀️',
                'облачно': '☁️',
                'дождь': '🌧️',
                'снег': '🌨️',
                'туман': '🌫️'
            }.get(desc.lower(), '🌤️')

            msg = f"{emoji} *Погода в {city.capitalize()}*\n\n"
            msg += f"🌡 Температура: {temp}°C (ощущается как {feels_like}°C)\n"
            msg += f"💧 Влажность: {humidity}%\n"
            msg += f"🌬 Ветер: {wind} м/с\n"
            msg += f"📝 {desc}"

            await sender.message.reply_text(msg, parse_mode='Markdown')
            log_action(user_id, "weather_check", city)
        else:
            await sender.message.reply_text("❌ Не удалось найти такой город. Попробуйте ещё раз.")
    except Exception as e:
        await sender.message.reply_text(f"❌ Ошибка: {str(e)}")


def _get_saved_cities(user_id):
    """Получить сохранённые города (заглушка — в продакшене из БД)"""
    # Временно: в памяти. Позже — таблица cities
    from bot.database import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT city FROM cities WHERE user_id = %s", (user_id,))
    cities = [row['city'] for row in cursor.fetchall()]
    conn.close()
    return cities


def _add_city(user_id, city):
    """Добавить город (в БД)"""
    from bot.database import get_db
    conn = get_db()
    cursor = conn.cursor()
    # Проверим премиум
    from bot.database import check_premium
    premium = check_premium(user_id)
    current_count = len(_get_saved_cities(user_id))
    if not premium and current_count >= 1:
        conn.close()
        return False, "Вы можете хранить только 1 город. Станьте премиум-пользователем!"
    if current_count >= 5:
        conn.close()
        return False, "Вы достигли лимита в 5 городов!"

    cursor.execute("""
        INSERT INTO cities (user_id, city, is_favorite)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
    """, (user_id, city, False))
    conn.commit()
    conn.close()
    return True, "Город добавлен!"


def _remove_city(user_id, city):
    """Удалить город"""
    from bot.database import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cities WHERE user_id = %s AND city = %s", (user_id, city))
    conn.commit()
    conn.close()
