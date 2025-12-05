from flask import Flask, request
import requests

app = Flask(__name__)

AI21_KEY = "0f2b2709-b2fc-4088-98dc-7c977dd591f0"

@app.post("/ai")
def ai():
    data = request.json
    if not data:
        return {"reply": "Нет данных"}, 400

    user_text = data.get("text", "")

    url = "https://api.ai21.com/studio/v1/j1-large/complete"

    headers = {
        "Authorization": f"Bearer {AI21_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "prompt": user_text,
        "numResults": 1,
        "maxTokens": 100,
        "temperature": 0.7
    }

    result = requests.post(url, json=body, headers=headers).json()
    reply = result["completions"][0]["data"]["text"]
    return {"reply": reply}
