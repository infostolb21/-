from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

responded_chats = set()

@app.post("/webhook")
async def webhook(request: Request):
    print("📥 Получен запрос")
    try:
        data = await request.json()
        print("📦 JSON:", data)
    except Exception as e:
        print("❌ Ошибка чтения JSON:", e)
        return {"error": "invalid_json"}

    try:
        message_data = data["payload"]["message"]
        chat_id = data["payload"]["chat_id"]
        message_text = message_data["text"]
        print(f"💬 Новое сообщение в чате {chat_id}: {message_text}")
    except KeyError as e:
        print("❌ Ошибка разбора полей:", e)
        return {"error": "'message'"}

    if chat_id in responded_chats:
        print("🔁 Уже отвечено в этот чат, пропускаем.")
        return {"status": "already_responded"}

    print("🔐 Получение access_token...")
    auth_response = requests.post(
        "https://api.avito.ru/token/",
        data={
            "grant_type": "client_credentials",
            "client_id": os.getenv("AVITO_CLIENT_ID"),
            "client_secret": os.getenv("AVITO_CLIENT_SECRET")
        }
    )

    if auth_response.status_code != 200:
        print("❌ Ошибка авторизации:", auth_response.text)
        return {"error": "auth_failed"}

    token = auth_response.json().get("access_token")
    print("✅ Токен получен")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    message = os.getenv("TEMPLATE_MESSAGE") or (
        "Здравствуйте! Мы занимаемся продажей Б/У опор и установкой. "
        "Работаем от 10 штук. Чтобы рассчитать стоимость, напишите, пожалуйста:
"
        "- Количество опор
"
        "- Длину
"
        "- Адрес доставки
"
        "- Ваш номер телефона
"
        "Если есть вопросы — с радостью ответим!"
    )

    payload = {
        "message": {
            "text": message
        }
    }

    send_url = f"https://api.avito.ru/messenger/v1/accounts/self/chats/{chat_id}/messages"
    print(f"📤 Отправляем автоответ в {chat_id}")
    print("📨 Тело:", payload)

    response = requests.post(send_url, headers=headers, json=payload)

    print("📬 Ответ Avito:", response.status_code, response.text)

    responded_chats.add(chat_id)

    return {"status": "ok", "avito_response": response.text}
