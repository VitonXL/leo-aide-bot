# web/routes.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()  # ← важно: именно router, не app

@router.get("/")
async def home():
    return {"message": "🌐 Веб работает!", "status": "ok"}

@router.get("/health")
async def health():
    return {"status": "ok"}
