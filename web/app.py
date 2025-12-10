# web/app.py
from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__, static_folder='static', template_folder='static')

# VirusTotal API
VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
VT_URL = "https://www.virustotal.com/api/v3/urls"

@app.route('/')
def index():
    # Принимаем параметры из Telegram Mini App
    user_id = request.args.get('user_id', '0')
    theme = request.args.get('theme', 'light')
    return render_template('index.html', user_id=user_id, theme=theme)

@app.route('/scan', methods=['POST'])
def scan_url():
    data = request.get_json()
    url = data.get('url', '').strip()

    if not url:
        return jsonify({"error": "URL не указан"}), 400

    try:
        # Проверка через VirusTotal
        headers = {
            "Authorization": f"Bearer {VT_API_KEY}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(VT_URL, headers=headers, data=f"url={url}")

        if response.status_code == 200:
            scan_id = response.json().get("data", {}).get("id")
            return jsonify({"success": True, "scan_id": scan_id})
        else:
            return jsonify({"error": "Ошибка VirusTotal"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/result/<scan_id>')
def get_result(scan_id):
    try:
        headers = {"Authorization": f"Bearer {VT_API_KEY}"}
        response = requests.get(f"https://www.virustotal.com/api/v3/analyses/{scan_id}", headers=headers)

        if response.status_code == 200:
            result = response.json()
            stats = result.get("data", {}).get("attributes", {}).get("stats", {})
            return jsonify({
                "status": result.get("data", {}).get("attributes", {}).get("status"),
                "stats": stats
            })
        else:
            return jsonify({"error": "Результат не найден"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Обслуживание статики
@app.route('/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
