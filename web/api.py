# web/api.py

from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter()

# 🔁 Замени на URL твоего бота (Railway)
BOT_API_URL = "https://leo-helper.up.railway.app"

@router.get("/user/{user_id}")
async def get_user_status(user_id: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BOT_API_URL}/api/user/{user_id}")
            if response.status_code == 200:
                data = response.json()
                return {
                    "role": data.get("role", "user"),
                    "premium_expires": data.get("premium_expires"),
                    "is_premium": data.get("role") == "premium"
                }
            else:
                raise HTTPException(status_code=404, detail="User not found")
        except Exception:
            return {"role": "user", "premium_expires": None, "is_premium": False}
