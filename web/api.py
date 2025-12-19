# web/api.py

import os
import asyncpg
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from loguru import logger

router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL не задана")

print(f"✅ DATABASE_URL: {DATABASE_URL[:30]}...")

db_pool = None


async def get_db_pool():
    global db_pool
    if db_pool is None:
        print("🔧 Создаём пул подключений к БД...")
        try:
            db_pool = await asyncpg.create_pool(DATABASE_URL, command_timeout=60)
            print("✅ Пул БД создан")
        except Exception as e:
            print(f"❌ Ошибка создания пула: {e}")
            raise
    return db_pool


async def get_user_data(user_id: int) -> Dict[str, Any]:
    print(f"🔍 Запрос данных для user_id = {user_id}")
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    id, first_name, username, language_code, 
                    role, premium_expires, theme
                FROM users 
                WHERE id = $1
            """, user_id)

            print(f"📄 Результат из БД: {row}")

            if not row:
                print("⚠️ Пользователь не найден в БД")
                return None

            referrals = await conn.fetchval("""
                SELECT COUNT(*) FROM referrals WHERE referrer_id = $1
            """, user_id)
            print(f"👥 Рефералов: {referrals}")

            return {
                "id": row["id"],
                "first_name": row["first_name"] or "Пользователь",
                "username": row["username"] or "unknown",
                "language": row["language_code"] or "ru",
                "role": row["role"] or "user",
                "premium_expires": row["premium_expires"].isoformat() if row["premium_expires"] else None,
                "is_premium": row["role"] == "premium",
                "referrals": referrals or 0,
                "theme": row["theme"] or "light"
            }
    except Exception as e:
        logger.error(f"❌ Ошибка в get_user_data: {e}")
        return None


@router.get("/user/{user_id}")
async def get_user_status(user_id: int):
    print(f"🌐 API: Получен запрос /api/user/{user_id}")
    try:
        user_data = await get_user_data(user_id)
        if not user_data:
            print("🔻 Возвращаем заглушку (пользователь не найден)")
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
        print(f"🟢 Успешно: возвращаем данные {user_data['first_name']} (@{user_data['username']})")
        return user_data
    except Exception as e:
        logger.error(f"💥 Ошибка в /api/user/{user_id}: {e}")
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


# === 🌙 Изменение темы ===
@router.post("/set-theme")
async def set_user_theme(user_id: int, theme: str, hash: str):
    if theme not in ["light", "dark"]:
        raise HTTPException(status_code=400, detail="Theme must be 'light' or 'dark'")

    from .utils import verify_cabinet_link
    if not verify_cabinet_link(user_id, hash):
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("UPDATE users SET theme = $1 WHERE id = $2", theme, user_id)
        return {"status": "success", "theme": theme}
    except Exception as e:
        logger.error(f"❌ Ошибка обновления темы: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


# === 🔐 АДМИН-ПАНЕЛЬ: Статистика ===
@router.get("/admin/stats")
async def get_admin_stats():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM users")
        premium = await conn.fetchval("SELECT COUNT(*) FROM users WHERE role = 'premium'")
        active_today = await conn.fetchval("""
            SELECT COUNT(*) FROM usage_stats 
            WHERE timestamp >= CURRENT_DATE
        """)
        referrals_count = await conn.fetchval("SELECT COUNT(*) FROM referrals")
    return {
        "total_users": total or 0,
        "premium_users": premium or 0,
        "active_today": active_today or 0,
        "referrals_count": referrals_count or 0
    }


@router.get("/admin/users")
async def get_all_users():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT 
                id, first_name, username, role, language_code as language, 
                premium_expires, last_seen
            FROM users
            ORDER BY last_seen DESC
            LIMIT 100
        """)
    return [dict(row) for row in rows]


@router.get("/admin/user")
async def get_single_user(query: str):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        if query.startswith('@'):
            user = await conn.fetchrow("SELECT * FROM users WHERE username = $1", query[1:])
        else:
            try:
                user_id = int(query)
                user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            except ValueError:
                return None
    return dict(user) if user else None


# === Премиум ===
@router.post("/admin/grant-premium")
async def api_grant_premium(user_id: int):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("""
            UPDATE users 
            SET role = 'premium', 
                premium_expires = NOW() + INTERVAL '30 days'
            WHERE id = $1
        """, user_id)
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": f"Премиум выдан пользователю {user_id}"}


@router.post("/admin/revoke-premium")
async def api_revoke_premium(user_id: int = Body(..., embed=True)):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users 
            SET premium_expires = NULL,
                role = CASE WHEN role = 'admin' THEN 'admin' ELSE 'user' END
            WHERE id = $1
        """, user_id)
    return {"status": "success", "message": f"Премиум снят с {user_id}"}


# === Активность ===
@router.get("/admin/activity-by-day")
async def get_activity_by_day():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT 
                DATE(timestamp) as day,
                COUNT(*) as count
            FROM usage_stats
            WHERE timestamp > NOW() - INTERVAL '30 days'
            GROUP BY day
            ORDER BY day
        """)
    return {
        "dates": [r["day"].isoformat() for r in rows],
        "counts": [r["count"] for r in rows]
    }


@router.get("/admin/top-commands")
async def get_top_commands():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT command, COUNT(*) as count
            FROM usage_stats
            GROUP BY command
            ORDER BY count DESC
            LIMIT 10
        """)
    return {
        "commands": [r["command"] for r in rows],
        "counts": [r["count"] for r in rows]
    }


# === Отзывы ===
@router.get("/admin/reviews")
async def get_reviews():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT 
                r.id, r.text, r.rating, r.created_at,
                u.id as user_id, u.first_name, u.username
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.is_approved = false
            ORDER BY r.created_at DESC
            LIMIT 50
        """)
    return [dict(r) for r in rows]


# === 🛠 ТЕХПОДДЕРЖКА: Тикеты ===

@router.get("/admin/support-tickets")
async def get_support_tickets():
    """
    Возвращает все открытые и в работе тикеты.
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, user_id, username, first_name, message, status, created_at
            FROM support_tickets
            WHERE status != 'resolved'
            ORDER BY created_at DESC
        """)
        return [
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "username": r["username"] or "unknown",
                "first_name": r["first_name"] or "Пользователь",
                "message": r["message"],
                "status": r["status"],
                "created_at": r["created_at"].isoformat()
            }
            for r in rows
        ]


@router.post("/admin/reply-support")
async def reply_support(
    ticket_id: int = Body(..., embed=True),
    reply_text: str = Body(..., embed=True)
):
    """
    Отправляет ответ пользователю и закрывает тикет.
    """
    from database import get_db_pool
    pool = await get_db_pool()

    # Получаем данные тикета
    async with pool.acquire() as conn:
        ticket = await conn.fetchrow(
            "SELECT user_id, message FROM support_tickets WHERE id = $1", ticket_id
        )
        if not ticket:
            raise HTTPException(status_code=404, detail="Тикет не найден")

    # Получаем бота
    try:
        from bot.main import application
        if not application:
            raise RuntimeError("❌ application не инициализирован")
        bot = application.bot
    except Exception as e:
        logger.error(f"❌ Не удалось получить бота: {e}")
        raise HTTPException(status_code=500, detail="Сервис бота недоступен")

    # Отправляем ответ
    try:
        await bot.send_message(
            ticket["user_id"],
            f"📬 Ответ от поддержки:\n\n{reply_text}\n\nСпасибо за обращение! ✅"
        )
        logger.info(f"✅ Ответ отправлен пользователю {ticket['user_id']} (тикет {ticket_id})")
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Ошибка отправки: {error_msg}")

        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE support_tickets SET status = 'in_progress', updated_at = NOW() WHERE id = $1",
                ticket_id
            )
        if "blocked" in error_msg.lower() or "not found" in error_msg.lower():
            raise HTTPException(status_code=500, detail="❌ Пользователь заблокировал бота")
        else:
            raise HTTPException(status_code=500, detail=f"❌ Ошибка отправки: {error_msg}")

    # Закрываем тикет
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE support_tickets SET status = 'resolved', updated_at = NOW() WHERE id = $1",
            ticket_id
        )
    logger.info(f"✅ Тикет {ticket_id} успешно закрыт")

    return {"status": "ok", "message": "Ответ отправлен, тикет закрыт"}