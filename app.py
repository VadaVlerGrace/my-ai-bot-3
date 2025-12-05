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

def extract_text_from_sendpulse(data):
    """Попытка безопасно достать текст из любого вида входящего JSON SendPulse"""
    if isinstance(data, list) and len(data) > 0:
        message_info = data[0].get("info", {}).get("message", {})
        # сначала ищем обычный текст
        if "message" in message_info and "text" in message_info["message"]:
            return message_info["message"]["text"]
        # если есть channel_data, проверяем там
        channel_text = message_info.get("channel_data", {}).get("message", {}).get("text")
        if channel_text:
            return channel_text
    return None

@app.route("/", methods=["POST"])
@app.route("/ai", methods=["POST"])
def ai():
    data = request.json
    user_text = extract_text_from_sendpulse(data)
    if not user_text:
        return jsonify({"error": "Не удалось извлечь текст"}), 400

    reply = get_ai21_reply(user_text)
    return jsonify({"reply": reply})
