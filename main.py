# main.py
import os
import logging
from threading import Thread

# Настройка логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Запуск бота
def run_bot():
    from bot.bot import main as bot_main
    bot_main()

# Запуск веб-сервера
def run_web():
    from web.app import app
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Запуск веба в отдельном потоке
    web_thread = Thread(target=run_web, daemon=True)
    web_thread.start()

    # Запуск бота (основной поток)
    run_bot()
