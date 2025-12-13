# bot/main.py
import logging
from telegram.ext import Application
from .config import BOT_TOKEN
from .database import create_db_pool, init_db
from .features import load_features  # <-- Автозагрузка модулей

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def post_init(application: Application):
    """Выполняется один раз при старте бота"""
    try:
        # Создаём пул подключений к БД
        pool = await create_db_pool()
        application.bot_data['pool'] = pool
        # Инициализируем таблицы
        await init_db(pool)
        # Загружаем все модули из features
        load_features(application)
        logger.info("✅ Бот успешно запущен и все модули загружены")
    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации: {e}")
        raise

def main():
    """Запуск бота"""
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)  # <-- Хук для инициализации
        .build()
    )
    application.run_polling()

if __name__ == "__main__":
    main()
