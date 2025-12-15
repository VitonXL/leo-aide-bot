# web/api.py

from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter()

# URL бота — должен совпадать с bot'ом
BOT_API_URL = os.getenv("BOT_API_URL", "https://mmuzs4kv.up.railway.app")


@router.get("/user/{user_id}")
async def get_user_status(user_id: int):
    """
    Возвращает полные данные пользователя для личного кабинета
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # 1. Получаем основные данные из бота (role, premium_expires)
            url = f"{BOT_API_URL.strip('/')}/api/user/{user_id}"
            response = await client.get(url)

            if response.status_code == 200:
                data = response.json()
            else:
                data = {}

            # 2. Получаем first_name, username, language_code из /users/{id}
            # Предположим, что бот также даёт доступ к данным пользователя
            user_url = f"{BOT_API_URL.strip('/')}/api/user/info/{user_id}"
            user_response = await client.get(user_url)

            if user_response.status_code == 200:
                user_info = user_response.json()
            else:
                user_info = {}

            # 3. Получаем количество рефералов
            referrals_url = f"{BOT_API_URL.strip('/')}/api/user/referrals/{user_id}"
            referrals_response = await client.get(referrals_url)
            if referrals_response.status_code == 200:
                referrals_count = referrals_response.json().get("count", 0)
            else:
                referrals_count = 0

            # 4. Формируем итоговый ответ
            return {
                "id": user_id,
                "first_name": user_info.get("first_name") or data.get("first_name") or "Пользователь",
                "username": user_info.get("username") or data.get("username") or "unknown",
                "role": data.get("role", "user"),
                "premium_expires": data.get("premium_expires"),
                "is_premium": data.get("role") == "premium",
                "language": user_info.get("language_code", "ru"),
                "theme": "light",  # можно сделать поле в БД позже
                "referrals": referrals_count
            }

        except httpx.ConnectError:
            return {
                "id": user_id,
                "first_name": "Пользователь",
                "username": "unknown",
                "role": "user",
                "premium_expires": None,
                "is_premium": False,
                "language": "ru",
                "theme": "light",
                "referrals": 0
            }
        except httpx.TimeoutException:
            return {
                "id": user_id,
                "first_name": "Пользователь",
                "username": "unknown",
                "role": "user",
                "premium_expires": None,
                "is_premium": False,
                "language": "ru",
                "theme": "light",
                "referrals": 0
            }
        except Exception:
            return {
                "id": user_id,
                "first_name": "Пользователь",
                "username": "unknown",
                "role": "user",
                "premium_expires": None,
                "is_premium": False,
                "language": "ru",
                "theme": "light",
                "referrals": 0
            }
