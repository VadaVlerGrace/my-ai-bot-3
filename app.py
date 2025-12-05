from flask import Flask, request
from ai21 import AI21Client
from ai21.models.chat import ChatMessage

app = Flask(__name__)

AI21_KEY = "0f2b2709-b2fc-4088-98dc-7c977dd591f0"

client = AI21Client(api_key=AI21_KEY)

@app.post("/ai")
def ai():
    data = request.json
    user_text = data.get("text", "")

    messages = [
        ChatMessage(role="user", content=user_text)
    ]

    response = client.chat.completions(
        model="jamba-instruct",
        messages=messages,
        max_tokens=100
    )

    reply = response.completions[0].message["content"]

    return {"reply": reply}
