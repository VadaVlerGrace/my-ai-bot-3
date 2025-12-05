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
    data = request.json
    user_text = data.get("text", "")

    if not user_text:
        return {"reply": "Пустой запрос"}, 400

    # Формируем сообщение
    messages = [
        ChatMessage(role="user", content=user_text)
    ]

    try:
        # Запрос к AI21
        response = client.chat.completions.create(
            model="jamba-instruct",  # модель AI21
            messages=messages,
            max_tokens=150
        )

        reply = response.choices[0].message.content
        return {"reply": reply}

    except Exception as e:
        return {"reply": f"Ошибка сервера: {e}"}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
