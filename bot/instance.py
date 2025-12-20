# bot/instance.py

from telegram.ext import Application

application = None
bot = None

def get_bot():
    if bot is None:
        raise RuntimeError("Бот ещё не инициализирован")
    return bot

def get_application():
    if application is None:
        raise RuntimeError("Application ещё не инициализирован")
    return application