from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
AI21_KEY = "0f2b2709-b2fc-4088-98dc-7c977dd591f0"

def get_ai21_reply(user_text):
    url = "https://api.ai21.com/studio/v1/j1-large/complete"
    headers = {"Authorization": f"Bearer {AI21_KEY}"}
    body = {
        "prompt": user_text,
        "maxTokens": 50,
        "temperature": 0.7
    }
    response = requests.post(url, json=body, headers=headers)
    result = response.json()
    return result["completions"][0]["data"]["text"]

@app.route("/", methods=["POST"])
@app.route("/ai", methods=["POST"])
def ai():
    data = request.json
    if isinstance(data, list) and len(data) > 0:
        try:
            user_text = data[0]["info"]["message"]["message"]["text"]
        except KeyError:
            return jsonify({"error": "Не удалось извлечь текст"}), 400
    else:
        return jsonify({"error": "Некорректный формат данных"}), 400

    if not user_text:
        return jsonify({"error": "Нет текста для обработки"}), 400

    reply = get_ai21_reply(user_text)
    return jsonify({"reply": reply})
