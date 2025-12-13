# web/routes.py

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import urllib.parse

from .utils import verify_webapp_data
import os

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Должен быть в переменных

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    theme = request.cookies.get("theme", "light")
    return templates.TemplateResponse("index.html", {"request": request, "theme": theme})

@router.post("/webapp", response_class=HTMLResponse)
async def handle_webapp(
    request: Request,
    user: str = Form(...),
    hash: str = Form(...)
):
    # Парсим данные пользователя
    parsed_user = urllib.parse.parse_qs(user)
    data_check_string = "&".join([f"{k}={v[0]}" for k, v in parsed_user.items()])
    
    # Проверяем подпись
    if not verify_webapp_data(BOT_TOKEN, data_check_string, hash):
        return HTMLResponse("❌ Подпись неверна! Доступ запрещён.", status_code=401)

    # Получаем данные
    user_data = eval(parsed_user["user"][0])  # {"id": 123, "first_name": "Иван", ...}
    theme = parsed_user.get("theme_params", ["{}"])[0]
    start_param = parsed_user.get("start_param", [""])[0]

    # Передаём в шаблон
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user_data,
            "theme": "dark" if theme.get("bg_color", "#ffffff").lower() in ["#000000", "#1a1a1a"] else "light"
        }
    )
