# web/api.py

from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter()

# Получаем URL бота из переменной окружения
# Если не задан — используем дефолтный Railway URL
BOT_API_URL = os.getenv("BOT_API_URL", "https://mmuzs4kv.up.railway.app")

@router.get("/user/{user_id}")
async def get_user_status(user_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Формируем URL: https://mmuzs4kv.up.railway.app/api/user/123456
            url = f"{BOT_API_URL.strip('/')}/api/user/{user_id}"
            
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "role": data.get("role", "user"),
                    "premium_expires": data.get("premium_expires"),
                    "is_premium": data.get("role") == "premium"
                }
            else:
                raise HTTPException(status_code=response.status_code, detail="User not found in bot")

        except httpx.ConnectError:
            return {"role": "user", "premium_expires": None, "is_premium": False}
        except httpx.TimeoutException:
            return {"role": "user", "premium_expires": None, "is_premium": False}
        except Exception as e:
            # Логировать ошибку можно позже
            return {"role": "user", "premium_expires": None, "is_premium": False}
