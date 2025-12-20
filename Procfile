web: uvicorn web.main:app --host 0.0.0.0 --port $PORT
bot: python -m bot.main
api: uvicorn bot.web_api:app --host 0.0.0.0 --port $PORT