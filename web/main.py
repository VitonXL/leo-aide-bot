# web/main.py
import sys
import os
import json
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, Request, APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

# Добавляем путь к корню проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="Лео Помощник — UI")

# --- Папки ---
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# --- Статика ---
static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# --- Шаблоны ---
templates = Jinja2Templates(directory=templates_dir)

# --- Роуты ---
try:
    from .routes import router as web_router
    app.include_router(web_router)
except Exception as e:
    logger.error(f"Ошибка импорта routes: {e}")

# --- API ---
try:
    from .api import router as api_router
    app.include_router(api_router)
except Exception as e:
    logger.error(f"Ошибка импорта api: {e}")

# --- Модераторский API ---
moderator_api = APIRouter(prefix="/api/moderator", tags=["moderator"])

@moderator_api.get("/tickets")
async def get_moderator_tickets():
    from .api import get_support_tickets
    return await get_support_tickets()

@moderator_api.post("/reply")
async def reply_via_moderator(data: dict):
    from .api import reply_ticket
    return await reply_ticket(ticket_id=data["ticket_id"], reply_text=data["reply_text"])

app.include_router(moderator_api)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    logger.info("🟢 Веб-сервер запущен")
    logger.info("✨ Роуты: /, /cabinet, /admin, /api/admin/stats, /api/moderator/tickets")