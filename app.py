from flask import Flask, request
from ai21 import AI21Client
from ai21.models.chat import ChatMessage

app = Flask(__name__)

# ТВОЙ ключ AI21
AI21_KEY = "0f2b2709-b2fc-4088-98dc-7c977dd591f0"

# Инициализация клиента
client = AI21Client(api_key=AI21_KEY)


@app.post("/ai")
def ai():
    data = request.json  # это список
    if not data:
        return {"reply": "Ошибка: нет данных"}, 400

    user_text = data[0].get("text", "")  # берем текст из первого элемента списка

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"

    body = {
        "contents": [
            {"parts": [{"text": user_text}]}
        ]
    }

    result = requests.post(url, json=body).json()
    reply = result["candidates"][0]["content"]["parts"][0]["text"]
    return {"reply": reply}


