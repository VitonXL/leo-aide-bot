# bot/commands/premium.py

from telegram import Update, LabeledPrice
from telegram.ext import ContextTypes, PreCheckoutQueryHandler

# ID продукта (можно хранить в БД)
PREMIUM_PRODUCT = {
    'title': 'Премиум-подписка',
    'description': 'Доступ ко всем функциям бота на 30 дней:\n'
                   '• Погода в 5 городах\n'
                   '• До 10 фильмов в день\n'
                   '• 5 запросов валют в день\n'
                   '• GigaChat (до 10 сообщений)\n'
                   '• Неограниченные напоминания',
    'payload': 'premium_30_days',
    'currency': 'XTR',  # Telegram Stars
    'prices': [LabeledPrice('Премиум на 30 дней', 10000)],  # 100 Stars = ~100 руб
    'start_parameter': 'premium'
}

async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=PREMIUM_PRODUCT['title'],
        description=PREMIUM_PRODUCT['description'],
        payload=PREMIUM_PRODUCT['payload'],
        provider_token='',  # не нужен для Stars
        currency=PREMIUM_PRODUCT['currency'],
        prices=PREMIUM_PRODUCT['prices'],
        start_parameter=PREMIUM_PRODUCT['start_parameter'],
        need_shipping_address=False,
        is_flexible=False,
        request_timeout=15
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload != PREMIUM_PRODUCT['payload']:
        await query.answer(ok=False, error_message="Что-то пошло не так...")
    else:
        await query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    from bot.database import set_premium, log_action
    set_premium(user_id, days=30)
    log_action(user_id, "premium_purchase", "30 days")
    await update.message.reply_text(
        "🎉 Поздравляем! Вам выдан премиум-доступ на 30 дней!\n"
        "Теперь вы можете использовать все функции бота."
    )
