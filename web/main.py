# web/main.py

from fastapi import FastAPI
from .routes import router

app = FastAPI(title="Лео Помощник — UI")

# Убрали временно app.mount — чтобы исключить ошибку
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}

# Добавим прямой маршрут — для проверки
@app.get("/test")
async def test():
    return {"test": "ok"}
