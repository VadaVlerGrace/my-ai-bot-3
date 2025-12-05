from flask import Flask, request, jsonify
import requests
import os

# --- КОНФИГУРАЦИЯ ---
app = Flask(__name__)

# Получение ключа API из переменных окружения.
# Это гораздо безопаснее, чем хранить ключ прямо в коде.
# На Render или в другом хостинге нужно установить переменную окружения 'AI21_KEY'.
AI21_KEY = os.getenv("0f2b2709-b2fc-4088-98dc-7c977dd591f0")

# Проверка наличия ключа при запуске
if not AI21_KEY:
    print("ВНИМАНИЕ: Переменная окружения 'AI21_KEY' не установлена. Бот не сможет работать.")
    # Для целей тестирования можно закомментировать print и установить тестовый ключ здесь:
    # AI21_KEY = "ВАШ_КЛЮЧ_ДЛЯ_ТЕСТИРОВАНИЯ"
# --------------------

def get_ai21_reply(user_text: str) -> str:
    """Отправляет запрос к AI21 Studio API и возвращает текст ответа."""
    if not AI21_KEY:
        return "Ошибка: Ключ AI21 API не настроен."

    url = "https://api.ai21.com/studio/v1/j1-large/complete"
    headers = {
        "Authorization": f"Bearer {AI21_KEY}",
        "Content-Type": "application/json"  # Явно указываем тип контента
    }
    body = {
        "prompt": user_text,
        "maxTokens": 100,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, json=body, headers=headers, timeout=15)
        response.raise_for_status() # Вызывает исключение для статусов 4xx/5xx
        
        result = response.json()
        
        if "completions" in result and len(result["completions"]) > 0:
            # Возвращаем сгенерированный текст
            return result["completions"][0]["data"]["text"].strip()
        else:
            # Логируем ответ API для отладки, если нет completions
            print(f"AI21 API не вернул completions: {result}")
            return "Ошибка: Модель не смогла сгенерировать ответ."
            
    except requests.exceptions.RequestException as e:
        # Обработка сетевых ошибок и ошибок HTTP (4xx, 5xx)
        print(f"Ошибка при запросе к AI21: {e}")
        return f"Ошибка API: {e}"
    except Exception as e:
        # Другие непредвиденные ошибки
        print(f"Непредвиденная ошибка: {e}")
        return f"Непредвиденная ошибка: {e}"

# --- ОБРАБОТЧИКИ ЗАПРОСОВ ---

# GET-запрос для проверки сервиса (работает ли веб-сервер)
@app.route("/", methods=["GET"])
def index():
    return "✅ Бот запущен. Отправляйте POST-запрос на /ai с JSON-телом {'text':'ваш текст'}"

# POST-запрос для основной логики бота
# Принимает запросы на /ai и / (если SendPulse не может настроить путь)
@app.route("/", methods=["POST"])
@app.route("/ai", methods=["POST"])
def ai():
    # 1. Попытка получить JSON данные
    data = request.json

    # Если request.json не сработал (например, отсутствует Content-Type: application/json),
    # пытаемся получить данные из формы (для совместимости с некоторыми конструкторами)
    if data is None:
        data = request.form.to_dict()
    
    # 2. Проверка наличия данных и поля "text"
    if not data or "text" not in data:
        # Эта ошибка 400 возникает, если SendPulse не отправляет JSON или данные формы с ключом 'text'.
        return jsonify({
            "error": "Нет текста для обработки. Ожидался JSON или форма с ключом 'text'.",
            "received_data": str(data) # Добавляем для отладки
        }), 400

    user_text = data["text"].strip()
    
    if not user_text:
        return jsonify({"error": "Текст пустой"}), 400

    # 3. Получение ответа от AI21
    reply = get_ai21_reply(user_text)
    
    # 4. Возвращаем JSON-ответ
    return jsonify({"reply": reply})

# --- ЗАПУСК ПРИЛОЖЕНИЯ ---

if __name__ == "__main__":
    # На Render и других хостингах используется переменная окружения PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
