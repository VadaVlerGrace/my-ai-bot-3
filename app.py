from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Ваш ключ AI21
AI21_KEY = "0f2b2709-b2fc-4088-98dc-7c977dd591f0"

def get_ai21_reply(user_text):
    """Отправка запроса к AI21 и безопасное получение ответа"""
    url = "https://api.ai21.com/studio/v1/j1-large/complete"
    headers = {"Authorization": f"Bearer {AI21_KEY}"}
    body = {
        "prompt": user_text,
        "maxTokens": 100,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, json=body, headers=headers, timeout=10)
        result = response.json()
        if "completions" in result and len(result["completions"]) > 0:
            return result["completions"][0]["data"]["text"]
        else:
            return "Ошибка: модель не вернула ответ"
    except Exception as e:
        return f"Ошибка при запросе к AI21: {e}"

@app.route("/ai", methods=["POST"])
@app.route("/", methods=["POST"])
def ai():
    """Обрабатываем POST-запрос с JSON {"text": "ваш текст"}"""
    data = request.json
    if not data or "text" not in data:
        return jsonify({"error": "Нет текста для обработки"}), 400

    user_text = data["text"].strip()
    if not user_text:
        return jsonify({"error": "Текст пустой"}), 400

    reply = get_ai21_reply(user_text)
    return jsonify({"reply": reply})

@app.route("/", methods=["GET"])
def index():
    """Просто проверка работоспособности сервиса"""
    return "Бот работает. Отправляйте POST-запрос на /ai или / с JSON {'text':'ваш текст'}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render требует динамический порт
    app.run(host="0.0.0.0", port=port)
