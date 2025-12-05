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

    # Проверяем, пришёл ли словарь или список
    if isinstance(data, dict):
        user_text = data.get("text", "")
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        user_text = data[0].get("text", "")
    else:
        user_text = ""

    if not user_text:
        return jsonify({"error": "Нет текста для обработки"}), 400

    try:
        reply = get_ai21_reply(user_text)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


