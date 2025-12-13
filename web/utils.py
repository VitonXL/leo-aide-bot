# web/utils.py

import hashlib
import hmac
from typing import Dict, Optional

def verify_webapp_data(token: str, data_check_string: str, hash: str) -> bool:
    """
    Проверяет подпись данных от Telegram Mini App.
    :param token: BOT_TOKEN (секретный ключ бота)
    :param data_check_string: строка данных, соединённая через &
    :param hash: хэш из параметров запроса
    :return: True, если подпись корректна
    """
    # Создаём секретный ключ из токена
    secret_key = hashlib.sha256(token.encode()).digest()
    
    # Сортируем параметры по имени
    data_check_list = data_check_string.split("&")
    data_check_list.sort()
    data_check_sorted = "\n".join(data_check_list)
    
    # Вычисляем hmac-sha256 и сравниваем с hash
    computed_hash = hmac.new(secret_key, data_check_sorted.encode(), hashlib.sha256).hexdigest()
    
    return computed_hash == hash
