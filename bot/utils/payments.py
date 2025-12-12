# bot/utils/payments.py

import hashlib
import os
from urllib.parse import urlencode

# Получаем ключи из переменных окружения
SHOP_ID = os.getenv("FK_SHOP_ID")
SECRET1 = os.getenv("FK_SECRET1")  # для ссылки
SECRET2 = os.getenv("FK_SECRET2")  # для callback

def create_payment_link(order_id: int, amount: float = 100.0):
    """Создаёт ссылку на оплату"""
    if not all([SHOP_ID, SECRET1]):
        raise ValueError("FK_SHOP_ID или FK_SECRET1 не заданы")

    params = {
        'm': SHOP_ID,
        'oa': amount,
        'o': order_id,
        's': '',  # подпись
        'currency': 'RUB',
        'lang': 'ru'
    }
    sign = f"{SHOP_ID}:{amount}:{SECRET1}:{order_id}"
    params['s'] = hashlib.md5(sign.encode()).hexdigest()
    return f"https://free-kassa.ru/merchant/cash.php?{urlencode(params)}"

def verify_payment(data: dict) -> bool:
    """Проверяет подпись платежа из Free-Kassa"""
    if not SECRET2:
        return False

    # Поля из Free-Kassa
    merchant_id = data['merchant_id']
    amount = data['amount']
    intid = data['intid']
    user_sign = data['sign'].lower()

    sign = f"{merchant_id}:{amount}:{SECRET2}:{intid}"
    correct_sign = hashlib.md5(sign.encode()).hexdigest()

    return correct_sign.lower() == user_sign
