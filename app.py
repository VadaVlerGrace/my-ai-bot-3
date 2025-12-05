from flask import Flask, request, jsonify
import requests
import os

# --- КОНФИГУРАЦИЯ ---
app = Flask(__name__)

# Использование переменной окружения для ключа API - ОБЯЗАТЕЛЬНО для Render
AI21_KEY = os.getenv("0f2b2709-b2fc-4088-98dc-7c977dd591f0") 
# ВНИМАНИЕ: На Render нужно установить переменную окружения AI21_KEY!
# --------------------

def get_ai21_reply(user_text: str) -> str:
    """Отправляет запрос к AI21 Studio API и возвращает текст ответа."""
    if not AI21_KEY:
        # Эта ошибка будет видна, если ключ не установлен в окружении
        return "Ошибка: Ключ AI21 API не настроен на сервере (AI21_KEY отсутствует)."

    url = "https://api.ai21.com/studio/v1/j1-large/complete"
    headers = {
        "Authorization": f"Bearer {AI21_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "prompt": user_text,
        "maxTokens": 100,
        "temperature": 0.7
    }
    
    try:
        # Увеличиваем таймаут на всякий случай
        response = requests.post(url, json=body, headers=headers, timeout=20)
        # Вызывает исключение для статусов 4xx/5xx, что позволяет поймать ошибку API
        response.raise_for_status() 
        
        result = response.json()
        
        if "completions" in result and len(result["completions"]) > 0:
            return result["completions"][0]["data"]["text"].strip()
        else:
            print(f"AI21 API не вернул completions: {result}")
            return "Ошибка: Модель не смогла сгенерировать ответ. Проверьте лимиты API."
            
    except requests.exceptions.HTTPError as err:
        # Ошибка, связанная с API (например, 401 Unauthorized, 429 Rate Limit)
        print(f"Ошибка HTTP при запросе к AI21: {err}")
        return f"Ошибка API: {response.status_code} - {err}"
    except requests.exceptions.RequestException as e:
        # Сетевые ошибки или таймаут
        print(f"Сетевая ошибка при запросе к AI21: {e}")
        return f"Ошибка сети/таймаута: {e}"
    except Exception as e:
        # Другие непредвиденные ошибки
        print(f"Непредвиденная ошибка в get_ai21_reply: {e}")
        return f"Непредвиденная ошибка: {e}"

# --- ОБРАБОТЧИКИ ЗАПРОСОВ ---

@app.route("/", methods=["GET"])
def index():
    """Проверка доступности сервиса."""
    return "✅ Бот запущен. Отправляйте POST-запрос на /ai или / с JSON-телом {'text':'ваш текст'}"

@app.route("/", methods=["POST"])
@app.route("/ai", methods=["POST"])
def ai():
    # Попытка получить данные как JSON
    data = request.json
    
    # ЕСЛИ JSON НЕ СРАБОТАЛ (нет Content-Type: application/json), 
    # пытаемся получить данные как ФОРМУ (application/x-www-form-urlencoded)
    if data is None:
        data = request.form.to_dict()
        print(f"Получены данные формы: {data}")
    else:
        print(f"Получены данные JSON: {data}")

    # Проверка наличия данных и поля "text"
    if not data or "text" not in data:
        # Это та самая ошибка 400. Теперь она дает больше информации.
        return jsonify({
            "error": "Нет текста для обработки. Ожидался ключ 'text' в JSON или данных формы.",
            "received_data": str(data),
            "content_type": request.content_type
        }), 400

    user_text = data["text"].strip()
    
    if not user_text:
        return jsonify({"error": "Текст пустой после очистки пробелов"}), 400

    # Получение ответа
    reply = get_ai21_reply(user_text)
    
    # Возвращаем JSON-ответ
    return jsonify({"reply": reply})

# --- ЗАПУСК ПРИЛОЖЕНИЯ ---

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    # Включаем отладку для локального тестирования
    app.run(host="0.0.0.0", port=port, debug=True)
