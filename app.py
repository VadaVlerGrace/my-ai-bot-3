from flask import Flask, request, jsonify
from ai21 import AI21Client
from ai21.models.completion import CompletionRequest

# Инициализация
API_KEY = "0f2b2709-b2fc-4088-98dc-7c977dd591f0"
client = AI21Client(api_key=API_KEY)
app = Flask(__name__)

@app.post("/ai")
def ai():
    data = request.json
    user_text = data.get("text", "")
    
    if not user_text:
        return jsonify({"reply": "Нет текста для обработки"}), 400

    try:
        # Запрос к AI21
        request_ai = CompletionRequest(
            model="j2-large",
            prompt=user_text,
            max_tokens=150
        )
        response = client.completions.create(request_ai)
        answer = response.completions[0].data.text.strip()
        
        return jsonify({"reply": answer})
    except Exception as e:
        return jsonify({"reply": f"Ошибка сервера: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
