# web/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import router

app = FastAPI(title="Лео Помощник — UI")

app.mount("/static", StaticFiles(directory="web/static"), name="static")
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}
