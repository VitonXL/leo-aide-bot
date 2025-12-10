from flask import Flask, request, jsonify
import requests
import threading
import os
import time

app = Flask(__name__)

VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

if not VIRUSTOTAL_API_KEY:
    raise RuntimeError("Не задан VIRUSTOTAL_API_KEY в переменных окружения")

scan_results = {}

@app.route('/scan/url', methods=['POST'])
def scan_url():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL не указан"}), 400

    vt_url = 'https://www.virustotal.com/vtapi/v2/url/scan'
    params = {'apikey': VIRUSTOTAL_API_KEY, 'url': url}
    try:
        response = requests.post(vt_url, data=params)
        result = response.json()
        if result.get('response_code') != 1:
            return jsonify({"error": result.get('verbose_msg', 'Ошибка сканирования')}), 400

        scan_id = result['scan_id']
        threading.Thread(target=poll_result, args=(scan_id, url), daemon=True).start()

        return jsonify({"scan_id": scan_id, "message": "Сканирование запущено"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scan/result/<scan_id>', methods=['GET'])
def get_result(scan_id):
    result = scan_results.get(scan_id)
    if result is None:
        return jsonify({"status": "processing"}), 202
    return jsonify(result), 200

def poll_result(scan_id, url):
    vt_url = 'https://www.virustotal.com/vtapi/v2/url/report'
    params = {'apikey': VIRUSTOTAL_API_KEY, 'resource': scan_id}
    for _ in range(20):
        try:
            response = requests.get(vt_url, params=params)
            result = response.json()
            if result.get('response_code') == 1:
                positives = result.get('positives', 0)
                total = result.get('total', 0)
                is_malicious = positives > 0

                scan_results[scan_id] = {
                    "status": "completed",
                    "is_malicious": is_malicious,
                    "positives": positives,
                    "total": total,
                    "url": url,
                    "scan_id": scan_id
                }
                return
        except:
            pass
        time.sleep(15)
    scan_results[scan_id] = {"status": "timeout"}

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
