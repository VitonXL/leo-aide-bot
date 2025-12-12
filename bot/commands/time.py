# bot/commands/time.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from datetime import datetime
import pytz
import requests
from bot.database import get_user, log_action

# Словарь часовых поясов (можно расширить)
TIMEZONES = {
    'UTC': 'UTC',
    'MSK': 'Europe/Moscow',
    'SAMT': 'Europe/Samara',
    'YEKT': 'Asia/Yekaterinburg',
    'OMST': 'Asia/Omsk',
    'KRAT': 'Asia/Krasnoyarsk',
    'IRKT': 'Asia/Irkutsk',
    'YAKT': 'Asia/Yakutsk',
    'VLAT': 'Asia/Vladivostok',
    'MAGT': 'Asia/Magadan',
    'PETT': 'Asia/Kamchatka',
    'ALMT': 'Asia/Almaty',
    'NOVT': 'Asia/Novosibirsk',
    'HKT': 'Asia/Hong_Kong',
    'TOKYO': 'Asia/Tokyo',
    'SYD': 'Australia/Sydney',
    'LON': 'Europe/London',
    'BER': 'Europe/Berlin',
    'MAD': 'Europe/Madrid',
    'IST': 'Asia/Kolkata',
    'NYC': 'America/New_York',
    'LAX': 'America/Los_Angeles',
}

# Кэш для IP-определения (временно)
user_ip_cache = {}

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await update.message.reply_text("Сначала начните бота: /start")
        return

    # Получаем сохранённый часовой пояс
    tz_name = user.get('timezone', 'Europe/Moscow')
    timezone = pytz.timezone(tz_name)
    now = datetime.now(timezone)

    # Клавиатура
    keyboard = [
        [InlineKeyboardButton("🔧 Изменить часовой пояс", callback_data="set_timezone")],
        [InlineKeyboardButton("📍 Определить по IP", callback_data="detect_ip_tz")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отображаемое имя
    tz_display = _get_tz_display(tz_name)

    await update.message.reply_text(
        f"🕒 *Точное время*\n\n"
        f"📍 Часовой пояс: `{tz_display}`\n"
        f"⏰ Сейчас: `{now.strftime('%H:%M:%S')}`\n"
        f"📅 Дата: `{now.strftime('%d.%m.%Y')}`",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    log_action(user_id, "check_time", tz_name)


async def time_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data == "set_timezone":
        await show_timezone_menu(query)
        await query.answer()

    elif data == "detect_ip_tz":
        await detect_timezone_by_ip(query, user_id)
        await query.answer()

    elif data.startswith("tz_"):
        tz_key = data.replace("tz_", "")
        tz_name = TIMEZONES.get(tz_key)
        if tz_name:
            from bot.database import get_db
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET timezone = %s WHERE user_id = %s", (tz_name, user_id))
            conn.commit()
            conn.close()

            timezone = pytz.timezone(tz_name)
            now = datetime.now(timezone)
            tz_display = _get_tz_display(tz_name)

            await query.message.edit_text(
                f"✅ Часовой пояс изменён на `{tz_display}`\n"
                f"⏰ Текущее время: `{now.strftime('%H:%M:%S')}`",
                parse_mode='Markdown'
            )
            log_action(user_id, "change_timezone", tz_name)


async def show_timezone_menu(query):
    """Показать меню выбора часового пояса"""
    keyboard = []
    row = []
    for i, (key, tz) in enumerate(TIMEZONES.items()):
        display = _get_tz_display(tz)
        row.append(InlineKeyboardButton(display, callback_data=f"tz_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_time")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text("🌍 Выберите часовой пояс:", reply_markup=reply_markup)


async def detect_timezone_by_ip(query, user_id):
    """Определить часовой пояс по IP"""
    if user_id in user_ip_cache:
        tz_name = user_ip_cache[user_id]
    else:
        try:
            response = requests.get("http://ip-api.com/json/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                region = data.get("region")
                # Упрощённое сопоставление
                tz_map = {
                    "RU-MOW": "Europe/Moscow",
                    "RU-SPE": "Europe/Samara",
                    "RU-KDA": "Europe/Moscow",
                    "RU-NVS": "Asia/Novosibirsk"
                }
                tz_name = tz_map.get(region, "Europe/Moscow")
                user_ip_cache[user_id] = tz_name
            else:
                tz_name = "Europe/Moscow"
        except:
            tz_name = "Europe/Moscow"

    # Обновляем в БД
    from bot.database import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET timezone = %s WHERE user_id = %s", (tz_name, user_id))
    conn.commit()
    conn.close()

    timezone = pytz.timezone(tz_name)
    now = datetime.now(timezone)
    tz_display = _get_tz_display(tz_name)

    await query.message.reply_text(
        f"📍 Определено по IP: `{tz_display}`\n"
        f"⏰ Текущее время: `{now.strftime('%H:%M:%S')}`",
        parse_mode='Markdown'
    )


def _get_tz_display(tz_name: str) -> str:
    """Упрощённое отображение часового пояса"""
    names = {
        'Europe/Moscow': 'Москва (MSK)',
        'Europe/Samara': 'Самара (SAMT)',
        'Asia/Yekaterinburg': 'Екатеринбург (YEKT)',
        'Asia/Omsk': 'Омск (OMST)',
        'Asia/Novosibirsk': 'Новосибирск (NOVT)',
        'Asia/Krasnoyarsk': 'Красноярск (KRAT)',
        'Asia/Irkutsk': 'Иркутск (IRKT)',
        'Asia/Yakutsk': 'Якутск (YAKT)',
        'Asia/Vladivostok': 'Владивосток (VLAT)',
        'Asia/Magadan': 'Магадан (MAGT)',
        'Asia/Kamchatka': 'Петропавловск-Камчатский (PETT)',
        'Asia/Almaty': 'Алматы (ALMT)',
        'Asia/Hong_Kong': 'Гонконг (HKT)',
        'Asia/Tokyo': 'Токио (TOKYO)',
        'Australia/Sydney': 'Сидней (SYD)',
        'Europe/London': 'Лондон (LON)',
        'Europe/Berlin': 'Берлин (BER)',
        'Europe/Madrid': 'Мадрид (MAD)',
        'Asia/Kolkata': 'Дели (IST)',
        'America/New_York': 'Нью-Йорк (NYC)',
        'America/Los_Angeles': 'Лос-Анджелес (LAX)',
        'UTC': 'UTC'
    }
    return names.get(tz_name, tz_name)
