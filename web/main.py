# web/main.py
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Лео Помощник — Web")

@app.get("/")
def read_root():
    return {"message": "Привет! Это веб-часть Лео помощника."}

@app.get("/health")
def health():
    return {"status": "ok"}

# Запуск: uvicorn web.main:app --host 0.0.0.0 --port $PORT
