# web/app.py

import os
from flask import Flask
from bot.database import get_user_count, get_premium_count, get_today_joined_count

app = Flask(__name__)

@app.route("/")
def home():
    try:
        total = get_user_count()
        premium = get_premium_count()
        today = get_today_joined_count()
    except Exception as e:
        return f"<h1>❌ Ошибка: {str(e)}</h1>"

    return f"""
    <html>
    <head><title>📊 Статистика Лео</title></head>
    <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h1>📈 Статистика бота Лео</h1>
        <p><b>Всего пользователей:</b> {total}</p>
        <p><b>Премиум:</b> {premium}</p>
        <p><b>Зашли сегодня:</b> {today}</p>
        <hr>
        <small>Обновляется в реальном времени</small>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
