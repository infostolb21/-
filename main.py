from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

# Память пользователей, которым уже отвечали
responded_users = set()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    # Проверим, есть ли нужные поля
    try:
        message_data = data["payload"]["message"]
        user_id = message_data["user_id"]
        chat_id = data["payload"]["chat_id"]
        message_text = message_data["text"]
    except KeyError:
        return {"error": "'message'"}

    # Чтобы бот отвечал только один раз
    if user_id in responded_users:
        return {"status": "already_answered"}

    # Получаем access_token
    auth_response = requests.post(
        "https://api.avito.ru/token/",
        data={
            "grant_type": "client_credentials",
            "client_id": os.getenv("AVITO_CLIENT_ID"),
            "client_secret": os.getenv("AVITO_CLIENT_SECRET")
        }
    )

    if auth_response.status_code != 200:
        return {"error": "auth_failed"}

    token = auth_response.json().get("access_token")

    # Отправка ответа
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    message = os.getenv("TEMPLATE_MESSAGE", "Здравствуйте!")

    payload = {
        "message": {
            "text": message
        }
    }

    send_url = f"https://api.avito.ru/messenger/v1/accounts/self/chats/{chat_id}/messages"

    response = requests.post(send_url, headers=headers, json=payload)

    # Отмечаем, что мы уже ответили этому пользователю
    responded_users.add(user_id)

    return {"status": "ok", "avito_response": response.text}
