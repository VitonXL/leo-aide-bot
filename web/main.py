# web/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import router

app = FastAPI(title="Лео Помощник — UI")

# Подключаем статику: /static/style.css
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Подключаем маршруты
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}
