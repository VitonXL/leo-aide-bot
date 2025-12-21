import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(f"🚀 ENV PORT: {os.getenv('PORT')}")
print(f"🚀 ARGS: {' '.join(os.sys.argv)}")
print("🔍 sys.path обновлен для импортов")

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from .routes import router
from .api import router as api_router
from loguru import logger

app = FastAPI(title="Лео Помощник — UI")

# 🔼 Сначала — статика
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# 🔽 Потом — API и роуты
app.include_router(api_router, prefix="/api")
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    logger.info("🟢 Веб-сервер запущен")
    logger.info("✨ Доступные роуты: /admin, /cabinet, /finance, /api/user/{id}")