# web/main.py
import os
print(f"🚀 ENV PORT: {os.getenv('PORT')}")
print(f"🚀 ARGS: {' '.join(os.sys.argv)}")
print("🔍 Добавляем корень в sys.path для импортов...")
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from .routes import router
from .api import router as api_router
from loguru import logger

app = FastAPI(title="Лео Помощник — UI")

# 🔼 Сначала — статика (чтобы /static/script.js отдавался напрямую)
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# 🔽 Потом — API и роуты
app.include_router(api_router, prefix="/api")
app.include_router(router)  # твои страницы (например, /cabinet)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    logger.info("🟢 Веб-сервер запущен")
    logger.info("✨ Роуты:")
    logger.info("  /admin — админ-панель")
    logger.info("  /cabinet — личный кабинет")
    logger.info("  /finance — финансы")
    logger.info("  /api/user/{id} — API статуса")
    logger.info("  /static/ — статика (CSS, JS)")
    logger.info("  /health — проверка состояния")

    hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if hostname:
        logger.info(f"🌐 Админка доступна: https://{hostname}/admin")