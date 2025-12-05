from flask import Flask, request, jsonify
import requests
import os

# --- КОНФИГУРАЦИЯ ---
app = Flask(__name__)

# Ключ AI21 API берется из переменной окружения
AI21_KEY = os.getenv("0f2b2709-b2fc-4088-98dc-7c977dd591f0") 
# ВНИМАНИЕ: На Render обязательно должна быть установлена переменная AI21_KEY!
# --------------------

def get_ai21_reply(user_text: str) -> str:
    """Отправляет запрос к AI21 Studio API и возвращает текст ответа."""
    if not AI21_KEY:
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
        response = requests.post(url, json=body, headers=headers, timeout=20)
        response.raise_for_status() 
        
        result = response.json()
        
        if "completions" in result and len(result["completions"]) > 0:
            return result["completions"][0]["data"]["text"].strip()
        else:
            print(f"AI21 API не вернул completions: {result}")
            # Возвращаем техническую ошибку, если модель не сгенерировала текст
            return "Ошибка модели: Не удалось получить ответ."
            
    except requests.exceptions.HTTPError as err:
        # Логируем ошибку 4xx/5xx от AI21
        print(f"Ошибка HTTP при запросе к AI21: {response.status_code} - {err}")
        return f"Ошибка API: Код {response.status_code}. Проверьте лимиты."
    except requests.exceptions.RequestException as e:
        # Сетевые ошибки или таймаут
        print(f"Сетевая ошибка при запросе к AI21: {e}")
        return f"Ошибка сети/таймаута: {e}"
    except Exception as e:
        print(f"Непредвиденная ошибка в get_ai21_reply: {e}")
        return f"Непредвиденная ошибка: {e}"

# --- ОБРАБОТЧИКИ ЗАПРОСОВ ---

@app.route("/", methods=["GET"])
def index():
    """Проверка доступности сервиса."""
    return "✅ Бот запущен. Отправляйте POST-запрос на /ai или /."

@app.route("/", methods=["POST"])
@app.route("/ai", methods=["POST"])
def ai():
    # 1. Сбор данных
    data = request.json
    if data is None:
        data = request.form.to_dict()
    
    print(f"Получены данные: {data}")

    # 2. Обработка массива вебхуков
    if isinstance(data, list) and data:
        webhook_data = data[0]
    elif isinstance(data, dict):
        webhook_data = data
    else:
        # Ошибка, если данные не в формате списка или словаря
        return jsonify({
            "error": "Неверный формат данных. Ожидался JSON-объект или массив.",
        }), 400
        
    # 3. ФИЛЬТРАЦИЯ ИСХОДЯЩИХ СООБЩЕНИЙ (НОВОЕ ИСПРАВЛЕНИЕ)
    if webhook_data.get('title') == 'исходящее_сообщение' or webhook_data.get('title') == 'outgoing_message':
        print("Игнорируем исходящее сообщение SendPulse. API не вызывается.")
        # Возвращаем 200 OK, чтобы SendPulse не ругался
        return jsonify({"status": "ignored", "reason": "Outgoing message"}), 200 

    # 4. Извлечение текста
    user_text = ""
    try:
        # Пытаемся получить текст из контактной информации (самый простой путь)
        if 'contact' in webhook_data and 'last_message' in webhook_data['contact']:
             user_text = webhook_data['contact']['last_message']
        
        # Если не сработало, пытаемся получить текст из основной структуры сообщения
        elif 'info' in webhook_data and 'message' in webhook_data['info'] and \
             'channel_data' in webhook_data['info']['message'] and 'message' in webhook_data['info']['message']['channel_data'] and \
             'text' in webhook_data['info']['message']['channel_data']['message']:
             
             user_text = webhook_data['info']['message']['channel_data']['message']['text']
        
        else:
            return jsonify({
                "error": "Не удалось найти текст в сложной структуре вебхука SendPulse. Отсутствует ключ 'last_message'."
            }), 400

    except Exception as e:
        print(f"Ошибка при парсинге данных SendPulse: {e}")
        return jsonify({"error": f"Ошибка при разборе вебхука: {e}"}), 400

    # 5. Очистка и проверка текста
    user_text = str(user_text).strip()
    
    if not user_text:
        return jsonify({"error": "Текст сообщения оказался пустым или None."}), 400

    # 6. Получение ответа от AI21
    reply = get_ai21_reply(user_text)
    
    # 7. Возвращаем JSON-ответ (КЛЮЧ "reply" ДОЛЖЕН БЫТЬ)
    return jsonify({"reply": reply})

# --- ЗАПУСК ПРИЛОЖЕНИЯ ---

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
