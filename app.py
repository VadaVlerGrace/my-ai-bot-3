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
    
    # Если JSON не сработал (редко, но возможно)
    if data is None:
        data = request.form.to_dict()

    print(f"Получены данные: {data}") # Оставляем для отладки

    # --- НОВАЯ ЛОГИКА ИЗВЛЕЧЕНИЯ ТЕКСТА ---
    user_text = ""
    try:
        # Ваш лог показал, что текст находится по пути:
        # data -> contact -> last_message
        if isinstance(data, dict) and 'contact' in data and 'last_message' in data['contact']:
             user_text = data['contact']['last_message']
        
        # Или, как запасной вариант (более глубокий путь из вашего JSON):
        elif isinstance(data, dict) and 'info' in data and 'message' in data['info'] and \
             'channel_data' in data['info']['message'] and 'message' in data['info']['message']['channel_data'] and \
             'text' in data['info']['message']['channel_data']['message']:
             
             user_text = data['info']['message']['channel_data']['message']['text']
        
        # Если ни один из вариантов не дал текст, возвращаем ошибку
        else:
            return jsonify({
                "error": "Не удалось найти текст в сложной структуре вебхука SendPulse.",
                "data_structure": "Ожидались ключи 'contact' -> 'last_message' или 'info' -> 'message' -> ... -> 'text'.",
                "received_keys": list(data.keys()) if isinstance(data, dict) else "Not a dict"
            }), 400

    except Exception as e:
        # Обработка ошибок, если структура данных внезапно изменится
        print(f"Ошибка при парсинге данных SendPulse: {e}")
        return jsonify({"error": f"Ошибка при разборе вебхука: {e}"}), 400

    # Очищаем и проверяем полученный текст
    user_text = str(user_text).strip()
    
    if not user_text:
        return jsonify({"error": "Текст сообщения оказался пустым или None."}), 400

    # --- ОСНОВНАЯ ЛОГИКА ---
    reply = get_ai21_reply(user_text)
    
    return jsonify({"reply": reply})

# Остальной код (app.route("/", methods=["GET"]), get_ai21_reply, __name__ == "__main__") 
# остается прежним из предыдущего ответа.

# --- ЗАПУСК ПРИЛОЖЕНИЯ ---

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    # Включаем отладку для локального тестирования
    app.run(host="0.0.0.0", port=port, debug=True)

