# web/app.py
from flask import Flask, request, jsonify, render_template_string
import os
import requests
import random
from datetime import datetime

app = Flask(__name__)

# === Настройки ===
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Цитаты
QUOTES = [
    "Лучше поздно, чем никогда.",
    "Начни с малого — но начни.",
    "Успех — это серия неудач без потери энтузиазма.",
    "Маленькие шаги каждый день ведут к большим результатам."
]

# Кэш новостей
_last_news = None
_last_news_time = None

# === Главная страница ===
@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>Leo Aide Mini-app</title>
        <style>
            body { font-family: -apple-system, sans-serif; padding: 20px; background: #f8f9fa; }
            .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin: 10px 0; }
            input, button, textarea { padding: 10px; margin: 5px 0; width: 100%; border: 1px solid #ddd; border-radius: 8px; }
            button { background: #0088cc; color: white; border: none; }
            ul { list-style: none; padding: 0; }
            li { padding: 8px 0; border-bottom: 1px solid #eee; }
            .admin-link { color: red; }
            .news-item { padding: 10px 0; border-bottom: 1px solid #eee; }
        </style>
    </head>
    <body>
        <h1>🌐 Leo Aide Mini-app</h1>
        <p>Всё в одном месте: погода, курсы, ИИ, новости.</p>

        <div class="card">
            <h2>🌤 Погода</h2>
            <input type="text" id="weather-city" placeholder="Город" />
            <button onclick="getWeather()">Узнать</button>
            <div id="weather-result"></div>
        </div>

        <div class="card">
            <h2>💸 Курсы валют</h2>
            <button onclick="getRates()">Обновить</button>
            <div id="rates-result">Загружаю...</div>
        </div>

        <div class="card">
            <h2>🧠 GigaChat</h2>
            <textarea id="ai-query" placeholder="Задайте вопрос..."></textarea>
            <button onclick="askAI()">Спросить</button>
            <div id="ai-result"></div>
        </div>

        <div class="card">
            <h2>🎮 Угадай число</h2>
            <input type="number" id="guess" placeholder="1-10" />
            <button onclick="playGame()">Играть</button>
            <div id="game-result"></div>
        </div>

        <div class="card">
            <h2>📰 Новости дня</h2>
            <button onclick="getNews()">Обновить</button>
            <div id="news-result">Загружаю...</div>
        </div>

        <div class="card">
            <h2>💬 Цитата дня</h2>
            <blockquote id="quote">Загружаю...</blockquote>
        </div>

        <div id="admin-section" style="display: none;">
            <a href="/admin" class="admin-link" target="_blank">🛠 Админ-панель</a>
        </div>

        <script>
            const urlParams = new URLSearchParams(window.location.search);
            const userId = urlParams.get('id');
            if (userId === '1799560429') {
                document.getElementById('admin-section').style.display = 'block';
            }

            async function getWeather() {
                const city = document.getElementById('weather-city').value;
                const res = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
                const data = await res.json();
                document.getElementById('weather-result').innerHTML = data.success ? 
                    `<b>${data.city}</b>: ${data.temp}°C, ${data.desc}` : 
                    `❌ ${data.error}`;
            }

            async function getRates() {
                const res = await fetch('/api/rates');
                const data = await res.json();
                document.getElementById('rates-result').innerHTML = `
                    💵 USD: ${data.usd} ₽<br>
                    💶 EUR: ${data.eur} ₽<br>
                    💎 TON: ${data.ton} $
                `;
            }

            async function askAI() {
                const query = document.getElementById('ai-query').value;
                document.getElementById('ai-result').innerHTML = '🧠 ...';
                const res = await fetch('/api/ai', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });
                const data = await res.json();
                document.getElementById('ai-result').innerHTML = data.answer || data.error;
            }

            async function playGame() {
                const guess = document.getElementById('guess').value;
                const res = await fetch('/api/game', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ guess: parseInt(guess) })
                });
                const data = await res.json();
                document.getElementById('game-result').innerHTML = data.message;
            }

            async function getNews() {
                const res = await fetch('/api/news');
                const data = await res.json();
                if (data.articles) {
                    document.getElementById('news-result').innerHTML = data.articles.map(a =>
                        `<div class="news-item">
                            <b>${a.title}</b><br>
                            <small>${a.source} · ${a.time}</small>
                        </div>`
                    ).join('');
                } else {
                    document.getElementById('news-result').innerHTML = '❌ Нет новостей';
                }
            }

            async function getQuote() {
                const res = await fetch('/api/quote');
                const data = await res.json();
                document.getElementById('quote').innerText = `"${data.quote}"`;
            }

            getRates(); getQuote(); getNews();
        </script>
    </body>
    </html>
    """
    return html

# === API ===
@app.route('/api/weather')
def api_weather():
    city = request.args.get('city')
    if not city: return jsonify({"success": False, "error": "Город не указан"})
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&lang=ru&units=metric"
    try:
        r = requests.get(url).json()
        return jsonify({
            "success": True,
            "city": r["name"],
            "temp": round(r["main"]["temp"]),
            "desc": r["weather"][0]["description"]
        })
    except: return jsonify({"success": False, "error": "Не найден"})

@app.route('/api/rates')
def api_rates():
    return jsonify({"usd": "91.20", "eur": "98.50", "ton": "2.15"})

@app.route('/api/ai', methods=['POST'])
def api_ai():
    return jsonify({"answer": "GigaChat в вебе пока через бота. Используйте команду /ai"})

@app.route('/api/game', methods=['POST'])
def api_game():
    data = request.get_json()
    guess = data.get("guess")
    number = random.randint(1, 10)
    msg = "🎉 Угадал!" if guess == number else f"❌ Нет. Загадано: {number}"
    return jsonify({"message": msg})

@app.route('/api/news')
def api_news():
    global _last_news, _last_news_time
    now = datetime.now()
    if _last_news and _last_news_time and (now - _last_news_time).seconds < 3600:
        return jsonify(_last_news)
    url = f"https://newsapi.org/v2/top-headlines?country=ru&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url).json()
        articles = [{"title": a["title"], "source": a["source"]["name"], "time": a["publishedAt"][:10]} for a in r["articles"][:3]]
        _last_news = {"articles": articles}
        _last_news_time = now
        return jsonify(_last_news)
    except: return jsonify({"articles": []})

@app.route('/api/quote')
def api_quote():
    return jsonify({"quote": random.choice(QUOTES)})

@app.route('/admin')
def admin_panel():
    user_id = request.args.get('id')
    if not user_id or int(user_id) != 1799560429: return "❌", 403
    return "<h1>🛠 Админ-панель</h1><p>Доступ получен!</p>"

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
