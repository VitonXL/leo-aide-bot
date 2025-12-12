# web/app.py

import os
from flask import Flask, request
import hashlib
from bot.database import set_premium, log_action
from bot.utils.payments import verify_payment

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

# 🌐 Callback от Free-Kassa
@app.route("/payment/callback", methods=["POST"])
def payment_callback():
    data = request.form.to_dict()

    # Проверяем подпись
    if not verify_payment(data):
        return "bad sign", 400

    order_id = int(data['inv_id'])
    amount = float(data['amount'])

    if amount < 100.0:
        return "invalid amount", 400

    # Проверяем заказ (в реальности — в БД)
    if order_id in pending_payments and pending_payments[order_id]['status'] == 'waiting':
        user_id = pending_payments[order_id]['user_id']
        set_premium(user_id, days=30)
        pending_payments[order_id]['status'] = 'paid'
        log_action(user_id, "premium_paid", f"order_id={order_id}")

        # Можно отправить сообщение в бота
        from telegram import Bot
        import os
        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        bot.send_message(user_id, "🎉 Премиум активирован! Спасибо за оплату 💙")

    return "OK", 200

# ⚠️ Глобальный словарь — временно (позже заменим на БД)
pending_payments = {}

# 🔽 Перенесём функции из database.py сюда, чтобы не было импорта
def get_user_count():
    from bot.database import get_user_count
    return get_user_count()

def get_premium_count():
    from bot.database import get_premium_count
    return get_premium_count()

def get_today_joined_count():
    from bot.database import get_today_joined_count
    return get_today_joined_count()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
