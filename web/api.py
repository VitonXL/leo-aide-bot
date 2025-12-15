# web/api.py

from fastapi import APIRouter, HTTPException
import asyncpg
import os
from typing import Dict, Any

router = APIRouter()

# Получаем DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("❌ Не задана DATABASE_URL")

# Глобальный пул подключений
db_pool = None


async def get_db_pool():
    """Создаёт и кэширует пул подключений к БД"""
    global db_pool
    if db_pool is None:
        try:
            db_pool = await asyncpg.create_pool(DATABASE_URL, command_timeout=60)
        except Exception as e:
            raise RuntimeError(f"❌ Не удалось подключиться к БД: {e}")
    return db_pool


async def get_user_data(user_id: int) -> Dict[str, Any]:
    """
    Получает данные пользователя из БД.
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Основные данные
        row = await conn.fetchrow("""
            SELECT 
                id, first_name, username, language_code, 
                role, premium_expires
            FROM users 
            WHERE id = $1
        """, user_id)

        if not row:
            return None

        # Количество рефералов
        referrals = await conn.fetchval("""
            SELECT COUNT(*) FROM referrals WHERE referrer_id = $1
        """, user_id)

        return {
            "id": row["id"],
            "first_name": row["first_name"] or "Пользователь",
            "username": row["username"] or "unknown",
            "language": row["language_code"] or "ru",
            "role": row["role"] or "user",
            "premium_expires": row["premium_expires"].isoformat() if row["premium_expires"] else None,
            "is_premium": row["role"] == "premium",
            "referrals": referrals or 0,
            "theme": "light"  # можно добавить поле позже
        }


@router.get("/user/{user_id}")
async def get_user_status(user_id: int):
    """
    Возвращает данные пользователя из БД напрямую.
    """
    try:
        user_data = await get_user_data(user_id)
        if not user_data:
            # Пользователь не найден
            return {
                "role": "user",
                "is_premium": False,
                "premium_expires": None,
                "first_name": "Пользователь",
                "username": "unknown",
                "language": "ru",
                "theme": "light",
                "referrals": 0
            }
        return user_data

    except Exception as e:
        print(f"❌ Ошибка при получении данных: {e}")
        return {
            "role": "user",
            "is_premium": False,
            "premium_expires": None,
            "first_name": "Пользователь",
            "username": "unknown",
            "language": "ru",
            "theme": "light",
            "referrals": 0
        }
