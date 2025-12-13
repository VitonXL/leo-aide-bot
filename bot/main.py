# bot/main.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.config import BOT_TOKEN
from bot.database import create_db_pool, init_db
from bot.features import load_features

import logging
from telegram.ext import Application

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Выполняется при старте
async def post_init(application):
    try:
        pool = await create_db_pool()
        application.bot_data['pool'] = pool
        await init_db(pool)
        load_features(application)
        logger.info("✅ Бот запущен, БД подключена, модули загружены")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации: {e}")
        raise
        
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
    # Создаём Application — центральный объект в v20+
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # Запуск polling
    application.run_polling()

if __name__ == "__main__":
    main()
