# bot/quotes.py
import random

QUOTES = [
    "Лучше поздно, чем никогда.",
    "Начни с малого — но начни.",
    "Успех — это серия неудач без потери энтузиазма.",
    "Маленькие шаги каждый день ведут к большим результатам."
]

def get_random_quote():
    return random.choice(QUOTES)
