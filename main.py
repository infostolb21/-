from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

responded_chats = set()

@app.post("/webhook")
async def webhook(request: Request):
    print("✅ Получен запрос на /webhook")
    try:
        data = await request.json()
        print("📦 Тело запроса:", data)
    except Exception as e:
        print("❌ Ошибка при чтении JSON:", e)
        return {"error": "invalid_json"}

    try:
        message_data = data["payload"]["message"]
        chat_id = data["payload"]["chat_id"]
        message_text = message_data["text"]
        print(f"💬 Получено сообщение: '{message_text}' в чате {chat_id}")
    except KeyError as e:
        print("❌ Ошибка при разборе сообщения:", e)
        return {"error": "'message'"}

    if chat_id in responded_chats:
        print("🔁 Бот уже отвечал в этот чат. Пропускаем.")
        return {"status": "already_responded_to_chat"}

    print("🔐 Получаем токен...")
    auth_response = requests.post(
        "https://api.avito.ru/token/",
        data={
            "grant_type": "client_credentials",
            "client_id": os.getenv("AVITO_CLIENT_ID"),
            "client_secret": os.getenv("AVITO_CLIENT_SECRET")
        }
    )

    if auth_response.status_code != 200:
        print("❌ Ошибка получения токена:", auth_response.text)
        return {"error": "auth_failed"}

    token = auth_response.json().get("access_token")
    print("✅ Токен получен")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    message = os.getenv("TEMPLATE_MESSAGE", "Здравствуйте! Мы занимаемся продажей Б/У опор. Работаем от 10 штук. Уточните, пожалуйста:
- Кол-во опор
- Длину
- Адрес доставки
- Ваш телефон
Если есть вопросы — пишите!")

    payload = {
        "message": {
            "text": message
        }
    }

    send_url = f"https://api.avito.ru/messenger/v1/accounts/self/chats/{chat_id}/messages"
    print("📤 Отправляем сообщение в чат:", send_url)
    print("📨 Тело:", payload)

    response = requests.post(send_url, headers=headers, json=payload)

    print("📬 Ответ от Avito:", response.status_code, response.text)

    responded_chats.add(chat_id)

    return {"status": "ok", "avito_response": response.text}
